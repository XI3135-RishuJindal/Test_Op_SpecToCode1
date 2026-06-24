      *================================================================*
      * ACCTAPI.cbl — Adapter: Primary/Driving Adapter (API Entry)   *
      * Hexagonal Architecture — Driving Adapter                      *
      * Exposes account operations to calling programs / CICS         *
      *================================================================*
       IDENTIFICATION DIVISION.
       PROGRAM-ID. ACCTAPI.
       AUTHOR.     ACCOUNT-MANAGEMENT-SERVICE.

       ENVIRONMENT DIVISION.
       CONFIGURATION SECTION.
       SOURCE-COMPUTER. IBM-MAINFRAME.
       OBJECT-COMPUTER. IBM-MAINFRAME.

       DATA DIVISION.
       WORKING-STORAGE SECTION.

       01 WS-ACCOUNT-RECORD.
          05 WS-ACCOUNT-ID        PIC X(10).
          05 WS-CUSTOMER-ID       PIC X(10).
          05 WS-ACCOUNT-TYPE      PIC X(02).
          05 WS-ACCOUNT-STATUS    PIC X(01).
          05 WS-ACCOUNT-BALANCE   PIC S9(13)V99 COMP-3.
          05 WS-OPEN-DATE         PIC X(08).
          05 WS-LAST-UPDATE       PIC X(08).

       01 WS-DOMAIN-OP            PIC X(10).
       01 WS-DOMAIN-RESULT        PIC X(02).
       01 WS-FILE-OP              PIC X(12).
       01 WS-FILE-RESULT          PIC X(02).

      *----------------------------------------------------------------*
      * Linkage Section — Public API contract                         *
      *----------------------------------------------------------------*
       LINKAGE SECTION.

       01 LS-REQUEST.
          05 LS-OPERATION         PIC X(10).
             88 OP-CREATE            VALUE 'CREATE    '.
             88 OP-READ              VALUE 'READ      '.
             88 OP-UPDATE            VALUE 'UPDATE    '.
             88 OP-DELETE            VALUE 'DELETE    '.
             88 OP-HEALTH            VALUE 'HEALTH    '.
          05 LS-ACCOUNT-ID        PIC X(10).
          05 LS-CUSTOMER-ID       PIC X(10).
          05 LS-ACCOUNT-TYPE      PIC X(02).
          05 LS-ACCOUNT-STATUS    PIC X(01).
          05 LS-ACCOUNT-BALANCE   PIC S9(13)V99 COMP-3.
          05 LS-OPEN-DATE         PIC X(08).
          05 LS-LAST-UPDATE       PIC X(08).

       01 LS-RESPONSE.
          05 LS-RESULT-CODE       PIC X(02).
             88 RESP-SUCCESS         VALUE '00'.
          05 LS-RESULT-MSG        PIC X(50).
          05 LS-RESP-ACCOUNT-ID   PIC X(10).
          05 LS-RESP-STATUS       PIC X(01).
          05 LS-RESP-BALANCE      PIC S9(13)V99 COMP-3.

       PROCEDURE DIVISION USING LS-REQUEST LS-RESPONSE.

       MAIN-LOGIC.
           INITIALIZE LS-RESPONSE

           EVALUATE TRUE
               WHEN OP-CREATE
                   PERFORM HANDLE-CREATE
               WHEN OP-READ
                   PERFORM HANDLE-READ
               WHEN OP-UPDATE
                   PERFORM HANDLE-UPDATE
               WHEN OP-DELETE
                   PERFORM HANDLE-DELETE
               WHEN OP-HEALTH
                   PERFORM HANDLE-HEALTH
               WHEN OTHER
                   MOVE '99' TO LS-RESULT-CODE
                   MOVE 'UNKNOWN OPERATION' TO LS-RESULT-MSG
           END-EVALUATE
           STOP RUN.

      *----------------------------------------------------------------*
      * HANDLE-HEALTH: Health check — always returns 00 / UP          *
      *----------------------------------------------------------------*
       HANDLE-HEALTH.
           MOVE '00' TO LS-RESULT-CODE
           MOVE 'SERVICE STATUS: UP' TO LS-RESULT-MSG.

      *----------------------------------------------------------------*
      * HANDLE-CREATE: Validate via domain, persist via file adapter  *
      *----------------------------------------------------------------*
       HANDLE-CREATE.
           MOVE LS-ACCOUNT-ID     TO WS-ACCOUNT-ID
           MOVE LS-CUSTOMER-ID    TO WS-CUSTOMER-ID
           MOVE LS-ACCOUNT-TYPE   TO WS-ACCOUNT-TYPE
           MOVE LS-ACCOUNT-STATUS TO WS-ACCOUNT-STATUS
           MOVE LS-ACCOUNT-BALANCE TO WS-ACCOUNT-BALANCE
           MOVE LS-OPEN-DATE      TO WS-OPEN-DATE
           MOVE LS-LAST-UPDATE    TO WS-LAST-UPDATE

           MOVE 'CREATE    '      TO WS-DOMAIN-OP
           CALL 'ACCTDMN' USING WS-ACCOUNT-RECORD
                                 WS-DOMAIN-OP
                                 WS-DOMAIN-RESULT

           IF WS-DOMAIN-RESULT NOT = '00'
               MOVE WS-DOMAIN-RESULT TO LS-RESULT-CODE
               MOVE 'DOMAIN VALIDATION FAILED' TO LS-RESULT-MSG
               GO TO HANDLE-CREATE-EXIT
           END-IF

           MOVE 'SAVE        '    TO WS-FILE-OP
           CALL 'ACCTFILE' USING WS-ACCOUNT-RECORD
                                 WS-FILE-OP
                                 WS-FILE-RESULT

           MOVE WS-FILE-RESULT    TO LS-RESULT-CODE
           IF WS-FILE-RESULT = '00'
               MOVE 'ACCOUNT CREATED' TO LS-RESULT-MSG
               MOVE WS-ACCOUNT-ID TO LS-RESP-ACCOUNT-ID
           ELSE
               MOVE 'FILE SAVE FAILED' TO LS-RESULT-MSG
           END-IF.

       HANDLE-CREATE-EXIT.
           EXIT.

      *----------------------------------------------------------------*
      * HANDLE-READ: Retrieve account by ID                           *
      *----------------------------------------------------------------*
       HANDLE-READ.
           MOVE LS-ACCOUNT-ID     TO WS-ACCOUNT-ID

           MOVE 'FIND-BY-ID  '    TO WS-FILE-OP
           CALL 'ACCTFILE' USING WS-ACCOUNT-RECORD
                                 WS-FILE-OP
                                 WS-FILE-RESULT

           MOVE WS-FILE-RESULT    TO LS-RESULT-CODE
           IF WS-FILE-RESULT = '00'
               MOVE 'ACCOUNT FOUND'     TO LS-RESULT-MSG
               MOVE WS-ACCOUNT-ID       TO LS-RESP-ACCOUNT-ID
               MOVE WS-ACCOUNT-STATUS   TO LS-RESP-STATUS
               MOVE WS-ACCOUNT-BALANCE  TO LS-RESP-BALANCE
           ELSE
               MOVE 'ACCOUNT NOT FOUND' TO LS-RESULT-MSG
           END-IF.

      *----------------------------------------------------------------*
      * HANDLE-UPDATE: Validate and overwrite existing account        *
      *----------------------------------------------------------------*
       HANDLE-UPDATE.
           MOVE LS-ACCOUNT-ID     TO WS-ACCOUNT-ID
           MOVE LS-CUSTOMER-ID    TO WS-CUSTOMER-ID
           MOVE LS-ACCOUNT-TYPE   TO WS-ACCOUNT-TYPE
           MOVE LS-ACCOUNT-STATUS TO WS-ACCOUNT-STATUS
           MOVE LS-ACCOUNT-BALANCE TO WS-ACCOUNT-BALANCE
           MOVE LS-OPEN-DATE      TO WS-OPEN-DATE
           MOVE LS-LAST-UPDATE    TO WS-LAST-UPDATE

           MOVE 'UPDATE    '      TO WS-DOMAIN-OP
           CALL 'ACCTDMN' USING WS-ACCOUNT-RECORD
                                 WS-DOMAIN-OP
                                 WS-DOMAIN-RESULT

           IF WS-DOMAIN-RESULT NOT = '00'
               MOVE WS-DOMAIN-RESULT TO LS-RESULT-CODE
               MOVE 'DOMAIN VALIDATION FAILED' TO LS-RESULT-MSG
               GO TO HANDLE-UPDATE-EXIT
           END-IF

           MOVE 'SAVE        '    TO WS-FILE-OP
           CALL 'ACCTFILE' USING WS-ACCOUNT-RECORD
                                 WS-FILE-OP
                                 WS-FILE-RESULT

           MOVE WS-FILE-RESULT    TO LS-RESULT-CODE
           IF WS-FILE-RESULT = '00'
               MOVE 'ACCOUNT UPDATED' TO LS-RESULT-MSG
           ELSE
               MOVE 'FILE UPDATE FAILED' TO LS-RESULT-MSG
           END-IF.

       HANDLE-UPDATE-EXIT.
           EXIT.

      *----------------------------------------------------------------*
      * HANDLE-DELETE: Remove account record                          *
      *----------------------------------------------------------------*
       HANDLE-DELETE.
           MOVE LS-ACCOUNT-ID     TO WS-ACCOUNT-ID

           MOVE 'DELETE      '    TO WS-FILE-OP
           CALL 'ACCTFILE' USING WS-ACCOUNT-RECORD
                                 WS-FILE-OP
                                 WS-FILE-RESULT

           MOVE WS-FILE-RESULT    TO LS-RESULT-CODE
           IF WS-FILE-RESULT = '00'
               MOVE 'ACCOUNT DELETED' TO LS-RESULT-MSG
           ELSE
               MOVE 'DELETE FAILED'   TO LS-RESULT-MSG
           END-IF.
