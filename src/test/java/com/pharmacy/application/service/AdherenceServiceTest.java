package com.pharmacy.application.service;

import com.pharmacy.application.port.in.RecordAdherenceCommand;
import com.pharmacy.application.port.out.AdherenceRepository;
import com.pharmacy.domain.exception.AdherenceRecordNotFoundException;
import com.pharmacy.domain.model.AdherenceRecord;
import com.pharmacy.domain.model.AdherenceStatus;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

/**
 * Unit tests for AdherenceService.
 */
@ExtendWith(MockitoExtension.class)
@DisplayName("AdherenceService")
class AdherenceServiceTest {

    @Mock
    private AdherenceRepository adherenceRepository;

    @InjectMocks
    private AdherenceService adherenceService;

    private AdherenceRecord pendingRecord;

    @BeforeEach
    void setUp() {
        pendingRecord = new AdherenceRecord(
                UUID.randomUUID(),
                "patient-001",
                UUID.randomUUID(),
                LocalDateTime.now().plusHours(1),
                null,
                AdherenceStatus.PENDING
        );
    }

    @Nested
    @DisplayName("recordAdherence")
    class RecordAdherence {

        @Test
        @DisplayName("creates and saves a PENDING adherence record")
        void recordAdherence_createsPendingRecord() {
            RecordAdherenceCommand command = new RecordAdherenceCommand(
                    "patient-001", UUID.randomUUID(), LocalDateTime.now().plusHours(1)
            );
            when(adherenceRepository.save(any(AdherenceRecord.class))).thenReturn(pendingRecord);

            AdherenceRecord result = adherenceService.recordAdherence(command);

            assertThat(result).isNotNull();
            assertThat(result.getAdherenceStatus()).isEqualTo(AdherenceStatus.PENDING);
            verify(adherenceRepository).save(any(AdherenceRecord.class));
        }
    }

    @Nested
    @DisplayName("markAsTaken")
    class MarkAsTaken {

        @Test
        @DisplayName("marks record as TAKEN with the given timestamp")
        void markAsTaken_setsStatusTaken() {
            UUID id = pendingRecord.getId();
            LocalDateTime takenAt = LocalDateTime.now();
            when(adherenceRepository.findById(id)).thenReturn(Optional.of(pendingRecord));
            when(adherenceRepository.save(any(AdherenceRecord.class))).thenReturn(pendingRecord);

            adherenceService.markAsTaken(id, takenAt);

            assertThat(pendingRecord.getAdherenceStatus()).isEqualTo(AdherenceStatus.TAKEN);
            assertThat(pendingRecord.getTakenTime()).isEqualTo(takenAt);
        }

        @Test
        @DisplayName("throws AdherenceRecordNotFoundException when record not found")
        void markAsTaken_throwsWhenNotFound() {
            UUID id = UUID.randomUUID();
            when(adherenceRepository.findById(id)).thenReturn(Optional.empty());

            assertThatThrownBy(() -> adherenceService.markAsTaken(id, LocalDateTime.now()))
                    .isInstanceOf(AdherenceRecordNotFoundException.class)
                    .hasMessageContaining(id.toString());
        }
    }

    @Nested
    @DisplayName("calculateAdherenceRate")
    class CalculateAdherenceRate {

        @Test
        @DisplayName("returns 0.0 when no records exist")
        void calculateAdherenceRate_returnsZeroWhenNoRecords() {
            when(adherenceRepository.findByPatientId("patient-001")).thenReturn(List.of());

            double rate = adherenceService.calculateAdherenceRate("patient-001");

            assertThat(rate).isEqualTo(0.0);
        }

        @Test
        @DisplayName("returns 100.0 when all records are TAKEN")
        void calculateAdherenceRate_returns100WhenAllTaken() {
            AdherenceRecord takenRecord = new AdherenceRecord(
                    UUID.randomUUID(), "patient-001", UUID.randomUUID(),
                    LocalDateTime.now(), LocalDateTime.now(), AdherenceStatus.TAKEN
            );
            when(adherenceRepository.findByPatientId("patient-001"))
                    .thenReturn(List.of(takenRecord));

            double rate = adherenceService.calculateAdherenceRate("patient-001");

            assertThat(rate).isEqualTo(100.0);
        }

        @Test
        @DisplayName("returns 50.0 when half of records are TAKEN")
        void calculateAdherenceRate_returns50WhenHalfTaken() {
            AdherenceRecord takenRecord = new AdherenceRecord(
                    UUID.randomUUID(), "patient-001", UUID.randomUUID(),
                    LocalDateTime.now(), LocalDateTime.now(), AdherenceStatus.TAKEN
            );
            AdherenceRecord missedRecord = new AdherenceRecord(
                    UUID.randomUUID(), "patient-001", UUID.randomUUID(),
                    LocalDateTime.now(), null, AdherenceStatus.MISSED
            );
            when(adherenceRepository.findByPatientId("patient-001"))
                    .thenReturn(List.of(takenRecord, missedRecord));

            double rate = adherenceService.calculateAdherenceRate("patient-001");

            assertThat(rate).isEqualTo(50.0);
        }
    }
}
