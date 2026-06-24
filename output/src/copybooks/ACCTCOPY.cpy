      *================================================================*
      * ACCTCOPY.cpy — Copybook: Shared Data Structures              *
      * Include with: COPY ACCTCOPY.                                  *
      *================================================================*

      *----------------------------------------------------------------*
      * Account Record — canonical layout shared across all programs  *
      *----------------------------------------------------------------*
       01 ACCT-RECORD.
          05 ACCT-ID              PIC X(10).
          05 ACCT-CUSTOMER-ID     PIC X(10).
          05 ACCT-TYPE            PIC X(02).
             88 ACCT-CHECKING        VALUE 'CH'.
             88 ACCT-SAVINGS         VALUE 'SV'.
             88 ACCT-LOAN            VALUE 'LN'.
          05 ACCT-STATUS          PIC X(01).
             88 ACCT-ACTIVE          VALUE 'A'.
             88 ACCT-CLOSED          VALUE 'C'.
             88 ACCT-FROZEN          VALUE 'F'.
          05 ACCT-BALANCE         PIC S9(13)V99 COMP-3.
          05 ACCT-OPEN-DATE       PIC X(08).
          05 ACCT-LAST-UPDATE     PIC X(08).

      *----------------------------------------------------------------*
      * Standard Result Code Layout                                   *
      *----------------------------------------------------------------*
       01 STD-RESULT.
          05 STD-RESULT-CODE      PIC X(02).
             88 STD-SUCCESS          VALUE '00'.
             88 STD-NOT-FOUND        VALUE '10'.
             88 STD-DUPLICATE        VALUE '11'.
             88 STD-IO-ERROR         VALUE '20'.
             88 STD-INVALID-DATA     VALUE '30'.
             88 STD-UNKNOWN-OP       VALUE '99'.
          05 STD-RESULT-MSG       PIC X(50).

      *----------------------------------------------------------------*
      * Health Response Layout                                        *
      *----------------------------------------------------------------*
       01 HEALTH-RESPONSE.
          05 HEALTH-STATUS        PIC X(04).
             88 HEALTH-UP            VALUE 'UP  '.
             88 HEALTH-DOWN          VALUE 'DOWN'.
          05 HEALTH-SERVICE-NAME  PIC X(30).
          05 HEALTH-VERSION       PIC X(10).
          05 HEALTH-TIMESTAMP     PIC X(26).
          05 HEALTH-RESULT-CODE   PIC X(02).
