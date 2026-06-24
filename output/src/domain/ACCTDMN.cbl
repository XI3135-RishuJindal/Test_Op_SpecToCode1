      *================================================================*
      * ACCTDMN.cbl — Domain: Account Management Core Logic           *
      * Hexagonal Architecture — Domain Layer (pure business rules)   *
      *================================================================*
       IDENTIFICATION DIVISION.
       PROGRAM-ID. ACCTDMN.
       AUTHOR.     ACCOUNT-MANAGEMENT-SERVICE.

       ENVIRONMENT DIVISION.
       CONFIGURATION SECTION.
       SOURCE-COMPUTER. IBM-MAINFRAME.
       OBJECT-COMPUTER. IBM-MAINFRAME.

       DATA DIVISION.
       WORKING-STORAGE SECTION.

      *----------------------------------------------------------------*
      * Account Record Structure (Domain Model)                        *
      *----------------------------------------------------------------*
       01 WS-ACCOUNT-RECORD.
          05 WS-ACCOUNT-ID        PIC X(10).
          05 WS-CUSTOMER-ID       PIC X(10).
          05 WS-ACCOUNT-TYPE      PIC X(02).
             88 ACCT-TYPE-CHECKING   VALUE 'CH'.
             88 ACCT-TYPE-SAVINGS    VALUE 'SV'.
             88 ACCT-TYPE-LOAN       VALUE 'LN'.
          05 WS-ACCOUNT-STATUS    PIC X(01).
             88 ACCT-STATUS-ACTIVE   VALUE 'A'.
             88 ACCT-STATUS-CLOSED   VALUE 'C'.
             88 ACCT-STATUS-FROZEN   VALUE 'F'.
          05 WS-ACCOUNT-BALANCE   PIC S9(13)V99 COMP-3.
          05 WS-OPEN-DATE         PIC X(08).
          05 WS-LAST-UPDATE       PIC X(08).

      *----------------------------------------------------------------*
      * Domain Result Codes                                            *
      *----------------------------------------------------------------*
       01 WS-DOMAIN-RESULT        PIC X(02).
          88 DOMAIN-SUCCESS          VALUE '00'.
          88 DOMAIN-INVALID-TYPE     VALUE '01'.
          88 DOMAIN-INVALID-STATUS   VALUE '02'.
          88 DOMAIN-NEGATIVE-BAL     VALUE '03'.
          88 DOMAIN-MISSING-ID       VALUE '04'.

      *----------------------------------------------------------------*
      * Linkage Section — Port Interface                               *
      *----------------------------------------------------------------*
       LINKAGE SECTION.
       01 LS-ACCOUNT-RECORD.
          05 LS-ACCOUNT-ID        PIC X(10).
          05 LS-CUSTOMER-ID       PIC X(10).
          05 LS-ACCOUNT-TYPE      PIC X(02).
          05 LS-ACCOUNT-STATUS    PIC X(01).
          05 LS-ACCOUNT-BALANCE   PIC S9(13)V99 COMP-3.
          05 LS-OPEN-DATE         PIC X(08).
          05 LS-LAST-UPDATE       PIC X(08).

       01 LS-OPERATION            PIC X(10).
       01 LS-RESULT-CODE          PIC X(02).

       PROCEDURE DIVISION USING LS-ACCOUNT-RECORD
                                 LS-OPERATION
                                 LS-RESULT-CODE.

       MAIN-LOGIC.
           EVALUATE LS-OPERATION
               WHEN 'VALIDATE'
                   PERFORM VALIDATE-ACCOUNT
               WHEN 'CREATE'
                   PERFORM CREATE-ACCOUNT
               WHEN 'UPDATE'
                   PERFORM UPDATE-ACCOUNT
               WHEN OTHER
                   MOVE '99' TO LS-RESULT-CODE
           END-EVALUATE
           STOP RUN.

      *----------------------------------------------------------------*
      * VALIDATE-ACCOUNT: Validate domain rules for an account record  *
      *----------------------------------------------------------------*
       VALIDATE-ACCOUNT.
           MOVE '00' TO LS-RESULT-CODE

           IF LS-ACCOUNT-ID = SPACES OR LS-ACCOUNT-ID = LOW-VALUES
               MOVE '04' TO LS-RESULT-CODE
               GO TO VALIDATE-ACCOUNT-EXIT
           END-IF

           IF LS-ACCOUNT-TYPE NOT = 'CH'
              AND LS-ACCOUNT-TYPE NOT = 'SV'
              AND LS-ACCOUNT-TYPE NOT = 'LN'
               MOVE '01' TO LS-RESULT-CODE
               GO TO VALIDATE-ACCOUNT-EXIT
           END-IF

           IF LS-ACCOUNT-STATUS NOT = 'A'
              AND LS-ACCOUNT-STATUS NOT = 'C'
              AND LS-ACCOUNT-STATUS NOT = 'F'
               MOVE '02' TO LS-RESULT-CODE
               GO TO VALIDATE-ACCOUNT-EXIT
           END-IF

           IF LS-ACCOUNT-BALANCE < 0
               MOVE '03' TO LS-RESULT-CODE
               GO TO VALIDATE-ACCOUNT-EXIT
           END-IF

       VALIDATE-ACCOUNT-EXIT.
           EXIT.

      *----------------------------------------------------------------*
      * CREATE-ACCOUNT: Apply creation defaults and validate           *
      *----------------------------------------------------------------*
       CREATE-ACCOUNT.
           IF LS-ACCOUNT-STATUS = SPACES
               MOVE 'A' TO LS-ACCOUNT-STATUS
           END-IF
           PERFORM VALIDATE-ACCOUNT.

      *----------------------------------------------------------------*
      * UPDATE-ACCOUNT: Validate updated account record                *
      *----------------------------------------------------------------*
       UPDATE-ACCOUNT.
           PERFORM VALIDATE-ACCOUNT.
