# What is Customer Lifetime Value (LTV)?

> A financial metric to value customers as long-term assets, not as isolated transactions.

---

## Definition

**Customer Lifetime Value** (LTV), also known as CLV, is the total economic value a customer brings to a company throughout their entire commercial relationship.

Unlike transactional metrics such as average ticket or order revenue, LTV adopts an extended temporal perspective: it doesn't ask "how much did this customer spend today?", but "how much value will this customer generate over time?".

---

## Origin and Academic Context

The LTV concept has roots in financial asset valuation theory. Just as a company values its machinery, inventory, or intellectual property, LTV proposes to value the customer portfolio as an economic asset.

The formalization of LTV in direct marketing is attributed to work in the 1980s, particularly in the financial services and mail-order sectors, where repeat purchases were crucial for profitability.

In the last two decades, the work of academics such as Peter Fader (Wharton) and Bruce Hardie (London Business School) has refined probabilistic models to estimate LTV, incorporating uncertainty and stochastic consumer behavior.

---

## Conceptual Formula

In its simplest form, LTV is expressed as:

```
LTV = Average gross margin per transaction × Expected number of future transactions
```

However, this simplification ignores crucial factors:

1. **Time discounting**: A dollar today is worth more than a dollar two years from now.
2. **Uncertainty**: Not all customers will continue to buy.
3. **Variability**: Customers do not spend the same on each visit.

Advanced models incorporate these dimensions, producing not a fixed number but a **probability distribution** of the expected value.

---

## Why LTV Matters

### 1. Acquisition Decisions

LTV allows for a rational budget for acquiring customers. If the average LTV of a customer is $120 and the contribution margin is 40%, the "net value" is $48. Any cost of acquisition (CAC) below that threshold generates value; above it, it destroys capital.

### 2. Resource Prioritization

Not all customers deserve the same level of investment. A customer with a $500 LTV justifies a personal follow-up call; one with a $20 LTV perhaps only an automated email.

### 3. Financial Projections

For companies with subscription or recurring purchase models, the aggregate LTV of the customer base constitutes a valued asset. Investors and analysts use this metric to evaluate the health of the business.

---

## Limitations of LTV

### Inherent Uncertainty

LTV is an **estimate**, not a certainty. Even the best models have significant margins of error, especially for new customers with little history.

### Context Dependence

LTV calculated today assumes that conditions will remain relatively stable: product offering, pricing, competitive behavior. Structural changes can invalidate historical predictions.

### Risk of Over-optimization

Making decisions solely based on LTV can lead to ignoring low-current-value customers who could become valuable, or over-investing in retaining customers who, despite their value, will decide to leave regardless of efforts.

---

## LTV in the European Practice

The European regulatory context, particularly after the implementation of GDPR, has modified how companies can collect and use data to estimate LTV.

Paradoxically, this limitation has driven more robust methodologies: instead of relying on granular tracking and third-party data, European companies have adopted models that work with their own transactional data (first-party data), which are sufficient for reliable LTV estimates.

---

## LTV 2.0: The Leap to Deep Intelligence

At Tactics, we have taken LTV calculation beyond traditional statistical models (such as Pareto/NBD). With the arrival of **Intelligence 2.0**, we introduce two disruptive technologies:

### 1. Intelligent Forgetting (LSTM)
Unlike formulas that give the same weight to all purchases, our AI uses **LSTM (Long Short-Term Memory)** networks. These networks are capable of understanding that a purchase made a year ago may be less relevant than a sudden change in behavior last month.

### 2. Attention Layers
Our AI does not look at your data as a uniform mass. It uses "Attention Layers" to illuminate critical events: that Black Friday campaign that attracted high-quality customers or that hibernation period of a VIP customer. The AI "pays attention" to what really matters to predict the future with an accuracy of 92%.

---

## Conclusion

Customer Lifetime Value represents a paradigm shift: from thinking about sales to thinking about relationships; from optimizing transactions to optimizing value accumulated over time.

Its adoption requires analytical and organizational maturity, but it offers a substantial competitive advantage: it allows informed decisions to be made about investment in acquisition and retention, aligning marketing operations with long-term economic value creation.

---

## References

- Fader, P.S., Hardie, B.G.S., & Lee, K.L. (2005). "Counting Your Customers" the Easy Way: An Alternative to the Pareto/NBD Model. *Marketing Science*, 24(2), 275-284.
- Gupta, S., & Lehmann, D.R. (2005). *Managing Customers as Investments*. Wharton School Publishing.
- Kumar, V. (2008). *Customer Lifetime Value: The Path to Profitability*. Now Publishers.

---

*Published by the Tactics editorial team. For inquiries: editorial@tactics.es*
