      *================================================================*
      * ACCTPORT.cbl — Port: Account Repository Port (Interface)      *
      * Hexagonal Architecture — Primary/Secondary Port Definition    *
      *================================================================*
       IDENTIFICATION DIVISION.
       PROGRAM-ID. ACCTPORT.
       AUTHOR.     ACCOUNT-MANAGEMENT-SERVICE.

       ENVIRONMENT DIVISION.
       CONFIGURATION SECTION.
       SOURCE-COMPUTER. IBM-MAINFRAME.
       OBJECT-COMPUTER. IBM-MAINFRAME.

       DATA DIVISION.
       WORKING-STORAGE SECTION.

      *----------------------------------------------------------------*
      * Port Operation Constants                                       *
      *----------------------------------------------------------------*
       01 WS-PORT-OPERATIONS.
          05 PORT-OP-FIND-BY-ID   PIC X(12) VALUE 'FIND-BY-ID  '.
          05 PORT-OP-FIND-BY-CUST PIC X(12) VALUE 'FIND-BY-CUST'.
          05 PORT-OP-SAVE         PIC X(12) VALUE 'SAVE        '.
          05 PORT-OP-DELETE       PIC X(12) VALUE 'DELETE      '.
          05 PORT-OP-LIST-ALL     PIC X(12) VALUE 'LIST-ALL    '.

      *----------------------------------------------------------------*
      * Port Result Codes                                              *
      *----------------------------------------------------------------*
       01 WS-PORT-RESULT-CODES.
          05 PORT-RC-SUCCESS      PIC X(02) VALUE '00'.
          05 PORT-RC-NOT-FOUND    PIC X(02) VALUE '10'.
          05 PORT-RC-DUPLICATE    PIC X(02) VALUE '11'.
          05 PORT-RC-IO-ERROR     PIC X(02) VALUE '20'.
          05 PORT-RC-INVALID-DATA PIC X(02) VALUE '30'.

      *----------------------------------------------------------------*
      * Shared Account Record Layout (used across all adapters)       *
      *----------------------------------------------------------------*
       01 WS-PORT-ACCOUNT-RECORD.
          05 PORT-ACCOUNT-ID      PIC X(10).
          05 PORT-CUSTOMER-ID     PIC X(10).
          05 PORT-ACCOUNT-TYPE    PIC X(02).
          05 PORT-ACCOUNT-STATUS  PIC X(01).
          05 PORT-ACCOUNT-BALANCE PIC S9(13)V99 COMP-3.
          05 PORT-OPEN-DATE       PIC X(08).
          05 PORT-LAST-UPDATE     PIC X(08).

       PROCEDURE DIVISION.
           STOP RUN.
