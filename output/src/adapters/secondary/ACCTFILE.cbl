      *================================================================*
      * ACCTFILE.cbl — Adapter: VSAM File Adapter (Secondary Port)   *
      * Hexagonal Architecture — Driven/Secondary Adapter             *
      *================================================================*
       IDENTIFICATION DIVISION.
       PROGRAM-ID. ACCTFILE.
       AUTHOR.     ACCOUNT-MANAGEMENT-SERVICE.

       ENVIRONMENT DIVISION.
       CONFIGURATION SECTION.
       SOURCE-COMPUTER. IBM-MAINFRAME.
       OBJECT-COMPUTER. IBM-MAINFRAME.

       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT ACCOUNT-FILE
               ASSIGN TO ACCTVSAM
               ORGANIZATION IS INDEXED
               ACCESS MODE IS DYNAMIC
               RECORD KEY IS AF-ACCOUNT-ID
               ALTERNATE RECORD KEY IS AF-CUSTOMER-ID
                   WITH DUPLICATES
               FILE STATUS IS WS-FILE-STATUS.

       DATA DIVISION.
       FILE SECTION.
       FD  ACCOUNT-FILE
           RECORD CONTAINS 80 CHARACTERS.
       01  ACCOUNT-FILE-RECORD.
           05 AF-ACCOUNT-ID        PIC X(10).
           05 AF-CUSTOMER-ID       PIC X(10).
           05 AF-ACCOUNT-TYPE      PIC X(02).
           05 AF-ACCOUNT-STATUS    PIC X(01).
           05 AF-ACCOUNT-BALANCE   PIC S9(13)V99 COMP-3.
           05 AF-OPEN-DATE         PIC X(08).
           05 AF-LAST-UPDATE       PIC X(08).
           05 FILLER               PIC X(22).

       WORKING-STORAGE SECTION.
       01 WS-FILE-STATUS           PIC X(02).
          88 FILE-SUCCESS             VALUE '00'.
          88 FILE-NOT-FOUND           VALUE '23'.
          88 FILE-DUPLICATE-KEY       VALUE '22'.
          88 FILE-END-OF-FILE         VALUE '10'.

       01 WS-FILE-OPEN-FLAG        PIC X(01) VALUE 'N'.
          88 FILE-IS-OPEN             VALUE 'Y'.
          88 FILE-IS-CLOSED           VALUE 'N'.

      *----------------------------------------------------------------*
      * Linkage Section — matches ACCTPORT interface                  *
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

       01 LS-OPERATION            PIC X(12).
       01 LS-RESULT-CODE          PIC X(02).

       PROCEDURE DIVISION USING LS-ACCOUNT-RECORD
                                 LS-OPERATION
                                 LS-RESULT-CODE.

       MAIN-LOGIC.
           IF FILE-IS-CLOSED
               OPEN I-O ACCOUNT-FILE
               MOVE 'Y' TO WS-FILE-OPEN-FLAG
           END-IF

           EVALUATE LS-OPERATION
               WHEN 'FIND-BY-ID  '
                   PERFORM FIND-BY-ID
               WHEN 'SAVE        '
                   PERFORM SAVE-ACCOUNT
               WHEN 'DELETE      '
                   PERFORM DELETE-ACCOUNT
               WHEN OTHER
                   MOVE '20' TO LS-RESULT-CODE
           END-EVALUATE

           CLOSE ACCOUNT-FILE
           MOVE 'N' TO WS-FILE-OPEN-FLAG
           STOP RUN.

      *----------------------------------------------------------------*
      * FIND-BY-ID: Read account record by primary key                *
      *----------------------------------------------------------------*
       FIND-BY-ID.
           MOVE LS-ACCOUNT-ID TO AF-ACCOUNT-ID
           READ ACCOUNT-FILE INTO LS-ACCOUNT-RECORD
               KEY IS AF-ACCOUNT-ID
               INVALID KEY
                   MOVE '10' TO LS-RESULT-CODE
               NOT INVALID KEY
                   MOVE '00' TO LS-RESULT-CODE
           END-READ.

      *----------------------------------------------------------------*
      * SAVE-ACCOUNT: Write or rewrite account record                 *
      *----------------------------------------------------------------*
       SAVE-ACCOUNT.
           MOVE LS-ACCOUNT-ID     TO AF-ACCOUNT-ID
           MOVE LS-CUSTOMER-ID    TO AF-CUSTOMER-ID
           MOVE LS-ACCOUNT-TYPE   TO AF-ACCOUNT-TYPE
           MOVE LS-ACCOUNT-STATUS TO AF-ACCOUNT-STATUS
           MOVE LS-ACCOUNT-BALANCE TO AF-ACCOUNT-BALANCE
           MOVE LS-OPEN-DATE      TO AF-OPEN-DATE
           MOVE LS-LAST-UPDATE    TO AF-LAST-UPDATE

           WRITE ACCOUNT-FILE-RECORD
               INVALID KEY
                   REWRITE ACCOUNT-FILE-RECORD
                       INVALID KEY
                           MOVE '20' TO LS-RESULT-CODE
                       NOT INVALID KEY
                           MOVE '00' TO LS-RESULT-CODE
                   END-REWRITE
               NOT INVALID KEY
                   MOVE '00' TO LS-RESULT-CODE
           END-WRITE.

      *----------------------------------------------------------------*
      * DELETE-ACCOUNT: Delete account record by primary key          *
      *----------------------------------------------------------------*
       DELETE-ACCOUNT.
           MOVE LS-ACCOUNT-ID TO AF-ACCOUNT-ID
           READ ACCOUNT-FILE
               KEY IS AF-ACCOUNT-ID
               INVALID KEY
                   MOVE '10' TO LS-RESULT-CODE
               NOT INVALID KEY
                   DELETE ACCOUNT-FILE RECORD
                       INVALID KEY
                           MOVE '20' TO LS-RESULT-CODE
                       NOT INVALID KEY
                           MOVE '00' TO LS-RESULT-CODE
                   END-DELETE
           END-READ.
