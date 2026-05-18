Repository: XI3135-RishuJindal/Test_Op_SpecToCode1

Workstream: Guardrails and Documentation
- [ ] add Tests/Policies/NoPaymentUiElementsTests.cs: implement a test that scans Controllers/ for disallowed keywords (payment, payments, billing, checkout, pay) in file names, class names, and route attributes; fail with a clear message listing offending files/lines.
- [ ] update README.md: add a statement under Overview clarifying that the MVP ships with no payment UI and that a policy test enforces this constraint.
- [ ] commit specs/remove-payment-ui-elements/spec.md, specs/remove-payment-ui-elements/