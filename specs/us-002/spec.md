WHAT
Implement CI dependency scanning for XI3135-RishuJindal/Test_Op_SpecToCode1 to automatically detect:
1) Use of payment-related SDKs/libraries in both backend (.NET) and any future frontend (Node) code, and
2) Known vulnerable dependencies in the repository and container/Docker context.

WHY
- Proactively enforce architecture and compliance policies restricting unapproved payment SDKs.
- Reduce risk from supply-chain vulnerabilities by scanning NuGet and (if present) Node ecosystems.
- Provide clear, automated feedback on PRs, preventing risky changes