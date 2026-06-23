# EXECUTIVE STRATEGIC REPORT: SUPPLY CHAIN & DELIVERY OPERATIONS ANALYTICS
**Project Title:** Supply Chain & Delivery Operations Analytics: SLA Performance, Seller Scorecard & Freight Intelligence Pipeline
**Reporting Period:** Sep 2016 – Aug 2018  |  **Analysis Framework:** SLA Tracking · Seller Scorecard · Freight Analysis · Customer Satisfaction

---

## 1. Executive Summary

An end-to-end operations analytics pipeline was executed across two years of real transactional data from Olist, Brazil's largest e-commerce marketplace aggregator, spanning 27 Brazilian states and 2,959 sellers. The pipeline evaluated **96,443 delivered orders representing R$13,215,255 in total revenue** across 57 product categories.

| KPI | Value |
|-----|-------|
| Total Orders Analysed | 96,443 |
| Total Revenue | R$13,215,255 |
| Unique Customers | 96,443 |
| Unique Sellers | 2,959 |
| Overall On-Time Delivery Rate | 93.2% |
| Avg Delay (Late Orders) | 10.3 days |
| Avg Customer Review Score | 4.16 / 5.0 |
| States Covered | 27 |
| Product Categories | 57 |
| MySQL Queries Executed | 7 |

---

## 2. Delivery Performance — Monthly Trend

| Period | Total Orders | On-Time Rate | Avg Review Score |
|--------|-------------|-------------|-----------------|
| 2017 Q1 | 13,422 | 91.8% | 4.09 |
| 2017 Q2 | 14,817 | 93.4% | 4.18 |
| 2017 Q3 | 16,481 | 93.6% | 4.19 |
| 2017 Q4 | 22,051 | 93.5% | 4.17 |
| 2018 Q1 | 20,268 | 93.8% | 4.22 |
| 2018 Q2 | 8,622 | 93.1% | 4.16 |

**Peak month:** November 2017 with 7,287 orders. On-time rate improved from 91.8% in Q1 2017 to 93.8% in Q1 2018, indicating improving operational maturity. Review scores correlate closely with on-time delivery — months with higher late rates consistently show lower satisfaction.

---

## 3. State-Level SLA Performance

### Highest SLA Breach States

| State | SLA Breach Rate | Avg Delivery Days | Avg Review Score |
|-------|----------------|-------------------|-----------------|
| AL (Alagoas) | 21.4% | 24.0 days | 3.85 |
| MA (Maranhao) | 17.4% | 21.1 days | 3.83 |
| SE (Sergipe) | 14.7% | 20.0 days | 3.92 |
| CE (Ceara) | 13.8% | 20.8 days | 3.94 |
| PI (Piaui) | 13.5% | 18.3 days | 3.99 |

### Lowest SLA Breach States

| State | SLA Breach Rate | Avg Delivery Days |
|-------|----------------|-------------------|
| AM (Amazonas) | 2.8% | — |
| RO (Rondonia) | 2.9% | — |
| PR (Parana) | 4.0% | — |
| SP (Sao Paulo) | 4.5% | — |
| MG (Minas Gerais) | 4.6% | — |

**Key pattern:** Northeast Brazil states (AL, MA, SE, CE, PI) consistently show the highest breach rates and lowest review scores. SP and MG — Brazil's largest economic hubs and likely warehouse concentration points — deliver the best SLA performance. The gap between best (2.8%) and worst (21.4%) is nearly 8x, indicating a structural logistics infrastructure gap rather than a demand or seller issue.

---

## 4. Customer Satisfaction by Delivery Speed

| Delivery Speed | Orders | Avg Review | Late Rate |
|---------------|--------|-----------|-----------|
| Express (1-7 days) | 33,526 | 4.41 / 5.0 | 0.3% |
| Standard (8-14 days) | 36,190 | 4.29 / 5.0 | 0.9% |
| Slow (15-21 days) | 15,264 | 4.10 / 5.0 | 4.2% |
| Very Slow (22+ days) | 10,818 | 3.01 / 5.0 | 48.9% |

**Critical finding:** Review score drops sharply from 4.10 to 3.01 when delivery exceeds 21 days — a 27% satisfaction collapse. The Very Slow bucket also carries a 48.9% late rate, meaning nearly half of these orders were delivered after the promised date. Express delivery (1-7 days) achieves a near-perfect 0.3% late rate and 4.41 review score, demonstrating that speed is the single largest driver of customer satisfaction in this marketplace.

---

## 5. Freight Cost Analysis by Product Category

### Highest Freight Burden Categories

| Category | Freight as % of Order Value | Avg Delivery Days | Avg Review |
|----------|---------------------------|-------------------|-----------|
| Christmas Supplies | 36.5% | 14.9 days | 4.11 |
| Signaling & Security | 30.4% | 10.4 days | 4.12 |
| Electronics | 29.5% | 12.5 days | 4.13 |
| Food & Drink | 29.5% | 10.5 days | 4.45 |
| DVDs & Blu-Ray | 27.1% | 12.5 days | 4.20 |

**Key insight:** Christmas Supplies carries the highest freight burden at 36.5% of order value — for every R$100 spent on products, R$36.50 is paid in freight. This is likely driven by bulky, fragile, or seasonal items that require special handling. Electronics and Food & Drink also carry high freight ratios despite reasonable delivery speeds, suggesting a pricing optimisation opportunity — either negotiate carrier rates for high-frequency categories or introduce minimum order thresholds to offset freight costs.

---

## 6. Seller Performance Scorecard

### Performance Tier Distribution

| Tier | Sellers | Criteria |
|------|---------|----------|
| Elite | 12 | Score >= 75: high on-time rate + high review + strong revenue |
| Good | 1,076 | Score 55-74 |
| Average | 134 | Score 35-54 |
| At Risk | 4 | Score < 35: chronic late delivery + low review scores |

### Revenue Concentration — Pareto Analysis

| Seller Group | Revenue | Share of Total |
|-------------|---------|---------------|
| Top 10 sellers | ~R$1,759,288 | 13.3% |
| Top 20 sellers | R$2,819,689 | 21.3% |
| At Risk sellers | R$32,934 | 0.25% |

**Key finding:** Revenue is relatively distributed across sellers — the top 20 account for 21.3% of total revenue, which is healthier than typical e-commerce marketplaces where top sellers often account for 50%+. However, the 4 At Risk sellers have a combined late rate exceeding 40% and review scores below 3.5, creating a brand risk disproportionate to their revenue contribution.

---

## 7. Strategic Recommendations

### Rec 1 — Regional Logistics Partnership for Northeast Brazil
- **Finding:** AL, MA, SE, CE, and PI consistently breach SLA at 13-21% rates with avg delivery exceeding 20 days. These states share poor last-mile infrastructure and limited carrier competition.
- **Recommendation:** Negotiate regional carrier partnerships or fulfilment centre agreements in Northeast Brazil. Even a 50% reduction in breach rate in these 5 states recovers approximately 800 orders per month from chronic late delivery.
- **Impact:** Direct improvement in Northeast customer satisfaction from 3.85 to 4.1+ review scores, reducing churn and increasing repeat purchase rates in a high-growth region.

### Rec 2 — Hard SLA Cap: Flag All 22+ Day Estimated Deliveries at Checkout
- **Finding:** Orders taking 22+ days carry a 48.9% late rate and 3.01 average review score. Customers who receive a 22+ day estimate at checkout are 5x more likely to leave a negative review than Express customers.
- **Recommendation:** Implement a checkout-time flag for any order with estimated delivery > 21 days, offering a compensation credit or discounted express upgrade. This shifts customer expectations before purchase rather than managing disappointment after delivery.
- **Impact:** Projected improvement in Very Slow bucket review score from 3.01 to 3.5+ and reduction in support escalations.

### Rec 3 — Freight Optimisation for High-Burden Categories
- **Finding:** Christmas Supplies (36.5%), Electronics (29.5%), and Food & Drink (29.5%) carry freight costs exceeding 29% of order value. These categories are price-sensitive and freight costs reduce competitiveness.
- **Recommendation:** Negotiate category-specific carrier contracts for high-volume, high-freight categories. Introduce free freight thresholds (e.g. free delivery on Electronics orders above R$200) to drive basket size while distributing freight cost.
- **Impact:** Estimated 8-12% increase in conversion rate for high-freight categories by reducing effective price premium.

### Rec 4 — At Risk Seller Intervention Programme
- **Finding:** 4 sellers classified as At Risk have composite scores below 35, driven by late rates above 40% and review scores below 3.5. While their revenue is low (R$32,934 combined), their operational failures create brand risk affecting marketplace trust.
- **Recommendation:** Issue a 30-day performance improvement notice to At Risk sellers with clear SLA targets. If targets are not met, restrict new order intake and escalate to seller review. Simultaneously, identify top-performing sellers in the same product categories to absorb volume.
- **Impact:** Eliminates the bottom 0.3% of revenue while protecting brand reputation. Prevents negative reviews from contaminating marketplace perception.

### Rec 5 — Express Delivery Incentive Programme
- **Finding:** Express delivery (1-7 days) achieves a 4.41 review score and 0.3% late rate. Standard delivery (8-14 days) drops to 4.29. Every additional week of delivery time costs approximately 0.1 points of review score.
- **Recommendation:** Introduce a seller incentive tied to Express delivery rate — sellers maintaining >30% of orders as Express delivery receive preferred marketplace placement and reduced commission rates. This aligns seller incentives with customer satisfaction outcomes.
- **Impact:** Increasing Express delivery share from current levels to 40% projected to raise overall marketplace review score from 4.16 to 4.25+.

---

## 8. Projected Impact Matrix

| Recommendation | Area | Expected Outcome |
|---------------|------|-----------------|
| Northeast Logistics Partnerships | AL, MA, SE, CE, PI | Breach rate from 17% to <9%; +800 on-time orders/month |
| 22+ Day Checkout Flag | Very Slow bucket (10,818 orders) | Review score 3.01 to 3.5+ |
| Freight Optimisation | Christmas, Electronics, Food | 8-12% conversion uplift in high-freight categories |
| At Risk Seller Intervention | 4 sellers | Brand risk elimination; volume redistributed to Elite sellers |
| Express Delivery Incentive | All sellers | Marketplace review score 4.16 to 4.25+ |

---

## 9. Next Steps

1. **Week 1-2:** Initiate carrier RFQ for Northeast Brazil regional logistics partnerships
2. **Week 2-3:** Deploy checkout-time flag for 22+ day estimated deliveries
3. **Month 1:** Issue performance improvement notices to 4 At Risk sellers
4. **Month 1-2:** Negotiate category-specific freight contracts for Electronics and Christmas Supplies
5. **Month 2:** Design and pilot Express Delivery Incentive programme with top 50 sellers
6. **Ongoing:** Re-run SLA breach analysis monthly; track seller tier migration and state-level improvement

---

*Dashboard: `outputs/power_bi_dashboard.png`*
*Full SQL Query Suite: `scripts/05_mysql_analytics.sql`*
*Pipeline: SLA Tracking · Seller Scorecard · Freight Analysis · Customer Satisfaction | Sep 2016 – Aug 2018*
*Dataset: Olist Brazilian E-Commerce — Olist (2018). Kaggle. https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce · CC BY-NC-SA 4.0*
