      *================================================================*
      * ACCTIMPT.cbl — Adapter: Customer Data Import Adapter          *
      * Hexagonal Architecture — Driven/Secondary Adapter             *
      * Responsibility: Import and update customer data from flat file *
      *================================================================*
       IDENTIFICATION DIVISION.
       PROGRAM-ID. ACCTIMPT.
       AUTHOR.     ACCOUNT-MANAGEMENT-SERVICE.

       ENVIRONMENT DIVISION.
       CONFIGURATION SECTION.
       SOURCE-COMPUTER. IBM-MAINFRAME.
       OBJECT-COMPUTER. IBM-MAINFRAME.

       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT IMPORT-FILE
               ASSIGN TO IMPORTIN
               ORGANIZATION IS SEQUENTIAL
               ACCESS MODE IS SEQUENTIAL
               FILE STATUS IS WS-IMPORT-STATUS.

       DATA DIVISION.
       FILE SECTION.
       FD  IMPORT-FILE
           RECORD CONTAINS 80 CHARACTERS.
       01  IMPORT-RECORD.
           05 IMP-ACCOUNT-ID      PIC X(10).
           05 IMP-CUSTOMER-ID     PIC X(10).
           05 IMP-ACCOUNT-TYPE    PIC X(02).
           05 IMP-ACCOUNT-STATUS  PIC X(01).
           05 IMP-BALANCE-STR     PIC X(15).
           05 IMP-OPEN-DATE       PIC X(08).
           05 IMP-LAST-UPDATE     PIC X(08).
           05 FILLER              PIC X(26).

       WORKING-STORAGE SECTION.
       01 WS-IMPORT-STATUS        PIC X(02).
          88 IMPORT-SUCCESS          VALUE '00'.
          88 IMPORT-EOF              VALUE '10'.

       01 WS-RECORDS-READ         PIC 9(07) VALUE ZEROS.
       01 WS-RECORDS-SAVED        PIC 9(07) VALUE ZEROS.
       01 WS-RECORDS-FAILED       PIC 9(07) VALUE ZEROS.

       01 WS-CALL-ACCOUNT-REC.
          05 WS-CALL-ACCT-ID      PIC X(10).
          05 WS-CALL-CUST-ID      PIC X(10).
          05 WS-CALL-ACCT-TYPE    PIC X(02).
          05 WS-CALL-ACCT-STATUS  PIC X(01).
          05 WS-CALL-BALANCE      PIC S9(13)V99 COMP-3.
          05 WS-CALL-OPEN-DATE    PIC X(08).
          05 WS-CALL-LAST-UPDATE  PIC X(08).

       01 WS-CALL-OPERATION       PIC X(12).
       01 WS-CALL-RESULT          PIC X(02).
       01 WS-BALANCE-NUMERIC      PIC S9(13)V99.

      *----------------------------------------------------------------*
      * Linkage Section — Import control parameters                   *
      *----------------------------------------------------------------*
       LINKAGE SECTION.
       01 LS-IMPORT-RESULT.
          05 LS-RECORDS-READ      PIC 9(07).
          05 LS-RECORDS-SAVED     PIC 9(07).
          05 LS-RECORDS-FAILED    PIC 9(07).
          05 LS-RESULT-CODE       PIC X(02).

       PROCEDURE DIVISION USING LS-IMPORT-RESULT.

       MAIN-LOGIC.
           MOVE ZEROS TO WS-RECORDS-READ
                         WS-RECORDS-SAVED
                         WS-RECORDS-FAILED

           OPEN INPUT IMPORT-FILE
           IF NOT IMPORT-SUCCESS
               MOVE '20' TO LS-RESULT-CODE
               STOP RUN
           END-IF

           PERFORM UNTIL IMPORT-EOF
               READ IMPORT-FILE INTO IMPORT-RECORD
                   AT END
                       CONTINUE
                   NOT AT END
                       ADD 1 TO WS-RECORDS-READ
                       PERFORM PROCESS-IMPORT-RECORD
               END-READ
           END-PERFORM

           CLOSE IMPORT-FILE

           MOVE WS-RECORDS-READ   TO LS-RECORDS-READ
           MOVE WS-RECORDS-SAVED  TO LS-RECORDS-SAVED
           MOVE WS-RECORDS-FAILED TO LS-RECORDS-FAILED
           MOVE '00'              TO LS-RESULT-CODE
           STOP RUN.

      *----------------------------------------------------------------*
      * PROCESS-IMPORT-RECORD: Validate and persist one import row    *
      *----------------------------------------------------------------*
       PROCESS-IMPORT-RECORD.
           MOVE IMP-ACCOUNT-ID    TO WS-CALL-ACCT-ID
           MOVE IMP-CUSTOMER-ID   TO WS-CALL-CUST-ID
           MOVE IMP-ACCOUNT-TYPE  TO WS-CALL-ACCT-TYPE
           MOVE IMP-ACCOUNT-STATUS TO WS-CALL-ACCT-STATUS
           MOVE IMP-OPEN-DATE     TO WS-CALL-OPEN-DATE
           MOVE IMP-LAST-UPDATE   TO WS-CALL-LAST-UPDATE

           MOVE FUNCTION NUMVAL(IMP-BALANCE-STR)
               TO WS-CALL-BALANCE

           MOVE 'VALIDATE    '    TO WS-CALL-OPERATION
           CALL 'ACCTDMN' USING WS-CALL-ACCOUNT-REC
                                 WS-CALL-OPERATION
                                 WS-CALL-RESULT

           IF WS-CALL-RESULT NOT = '00'
               ADD 1 TO WS-RECORDS-FAILED
               GO TO PROCESS-IMPORT-RECORD-EXIT
           END-IF

           MOVE 'SAVE        '    TO WS-CALL-OPERATION
           CALL 'ACCTFILE' USING WS-CALL-ACCOUNT-REC
                                 WS-CALL-OPERATION
                                 WS-CALL-RESULT

           IF WS-CALL-RESULT = '00'
               ADD 1 TO WS-RECORDS-SAVED
           ELSE
               ADD 1 TO WS-RECORDS-FAILED
           END-IF.

       PROCESS-IMPORT-RECORD-EXIT.
           EXIT.
