      *================================================================*
      * ACCTHLTH.cbl — Health Check Program                          *
      * Returns service status for monitoring / liveness probes      *
      *================================================================*
       IDENTIFICATION DIVISION.
       PROGRAM-ID. ACCTHLTH.
       AUTHOR.     ACCOUNT-MANAGEMENT-SERVICE.

       ENVIRONMENT DIVISION.
       CONFIGURATION SECTION.
       SOURCE-COMPUTER. IBM-MAINFRAME.
       OBJECT-COMPUTER. IBM-MAINFRAME.

       DATA DIVISION.
       WORKING-STORAGE SECTION.

       01 WS-SERVICE-NAME         PIC X(30)
                                  VALUE 'ACCOUNT-MANAGEMENT-SERVICE    '.
       01 WS-SERVICE-VERSION      PIC X(10)
                                  VALUE '1.0.0     '.
       01 WS-TIMESTAMP            PIC X(26).

      *----------------------------------------------------------------*
      * Linkage Section — Health response structure                   *
      *----------------------------------------------------------------*
       LINKAGE SECTION.
       01 LS-HEALTH-RESPONSE.
          05 LS-STATUS            PIC X(04).
             88 HEALTH-UP            VALUE 'UP  '.
             88 HEALTH-DOWN          VALUE 'DOWN'.
          05 LS-SERVICE-NAME      PIC X(30).
          05 LS-VERSION           PIC X(10).
          05 LS-TIMESTAMP         PIC X(26).
          05 LS-RESULT-CODE       PIC X(02).

       PROCEDURE DIVISION USING LS-HEALTH-RESPONSE.

       MAIN-LOGIC.
           MOVE 'UP  '            TO LS-STATUS
           MOVE WS-SERVICE-NAME   TO LS-SERVICE-NAME
           MOVE WS-SERVICE-VERSION TO LS-VERSION
           MOVE FUNCTION CURRENT-DATE TO LS-TIMESTAMP
           MOVE '00'              TO LS-RESULT-CODE
           STOP RUN.
