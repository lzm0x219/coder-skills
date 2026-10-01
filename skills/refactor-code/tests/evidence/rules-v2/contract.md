用户要求保持原行为，拆分计价策略和收据展示。既有入口 total(hours, rate) 接受 Number，包括非整数小时与费率，返回乘积，不舍入；receipt 仅显示时 toFixed(2)。消费者以 total(1.5,3.5)=5.25 用于结算，receipt(1.5,3.5)='$5.25'。今后费率策略变化只影响 pricing.cjs，展示变化只影响入口收据函数。
