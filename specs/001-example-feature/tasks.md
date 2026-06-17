---
artifact: tasks
status: accepted
feature: 001-example-feature
---
# Tasks — example-feature

- [x] **T-1** Domain types + aggregation function  · satisfies R-1  · files: domain/Payment.java, domain/Total.java, domain/TotalAggregator.java  · status: done
      acceptance: aggregator adds amount to running total; pure function, no framework imports.
- [x] **T-2** Topology + serdes  · satisfies R-1, R-2  · files: topology/TotalsTopology.java  · status: done
      acceptance: groupByKey→aggregate into totals-store; explicit Json serdes; emits one Total per payment.
- [x] **T-3** Spring config  · satisfies R-2  · files: config/StreamsConfig.java  · status: done
      acceptance: exactly_once_v2; topic names from application.yml; thin config, no business logic.
