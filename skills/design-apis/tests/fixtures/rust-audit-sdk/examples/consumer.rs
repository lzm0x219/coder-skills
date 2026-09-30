//! 只编译调用点；不运行未实现的 SDK 入口。

use audit_sdk_design::{
    AccessToken, AuditClient, AuditError, AuditErrorKind, ConfigError, CredentialError,
    CredentialProvider, ListEvents, PageSize, TokenFuture,
};
use std::future::Future;
use std::sync::Arc;
use std::time::Duration;

struct DemoCredentials {
    value: String,
}

impl CredentialProvider for DemoCredentials {
    fn token(&self) -> TokenFuture<'_> {
        Box::pin(async move {
            AccessToken::new(self.value.clone()).map_err(|_| CredentialError::Unavailable)
        })
    }
}

pub fn make_client(endpoint: &str, token: String) -> Result<AuditClient, ConfigError> {
    AuditClient::builder(endpoint, Arc::new(DemoCredentials { value: token }))
        .timeout(Duration::from_secs(5))
        .build()
}

fn require_send_sync<T: Send + Sync>() {}
fn require_send_future<F: Future + Send>(_: F) {}

pub fn check_thread_contract(client: &AuditClient) {
    require_send_sync::<AuditClient>();
    require_send_sync::<ListEvents>();
    require_send_future(client.list_page(ListEvents::first_page(PageSize::DEFAULT)));
}

pub async fn fetch_two_pages(
    client: &AuditClient,
    on_rate_limit: impl Fn(Option<Duration>),
    on_unauthorized: impl Fn(),
) -> Result<Vec<String>, AuditError> {
    let mut next = Some(ListEvents::first_page(PageSize::DEFAULT));
    let mut ids = Vec::new();
    for _ in 0..2 {
        let Some(request) = next else { break };
        let page = match client.list_page(request).await {
            Ok(page) => page,
            Err(error) => {
                match error.kind() {
                    AuditErrorKind::RateLimited => on_rate_limit(error.retry_after()),
                    AuditErrorKind::Unauthorized => on_unauthorized(),
                    _ => {} // 包括未来新增的错误类别。
                }
                return Err(error);
            }
        };
        ids.extend(page.events().iter().map(|event| event.id().to_owned()));
        next = page.next_request();
    }
    Ok(ids)
}

fn main() {}
