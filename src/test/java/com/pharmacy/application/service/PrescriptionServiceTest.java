package com.pharmacy.application.service;

import com.pharmacy.application.port.in.CreatePrescriptionCommand;
import com.pharmacy.application.port.out.PrescriptionRepository;
import com.pharmacy.domain.exception.PrescriptionNotFoundException;
import com.pharmacy.domain.model.Prescription;
import com.pharmacy.domain.model.PrescriptionStatus;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

/**
 * Unit tests for PrescriptionService.
 */
@ExtendWith(MockitoExtension.class)
@DisplayName("PrescriptionService")
class PrescriptionServiceTest {

    @Mock
    private PrescriptionRepository prescriptionRepository;

    @InjectMocks
    private PrescriptionService prescriptionService;

    private Prescription activePrescription;

    @BeforeEach
    void setUp() {
        activePrescription = new Prescription(
                UUID.randomUUID(),
                "patient-001",
                "Amoxicillin",
                "500mg",
                30,
                3,
                LocalDate.now(),
                LocalDate.now().plusYears(1),
                PrescriptionStatus.ACTIVE
        );
    }

    @Nested
    @DisplayName("createPrescription")
    class CreatePrescription {

        @Test
        @DisplayName("saves and returns a new ACTIVE prescription")
        void createPrescription_savesAndReturnsActivePrescription() {
            CreatePrescriptionCommand command = new CreatePrescriptionCommand(
                    "patient-001", "Amoxicillin", "500mg", 30, 3,
                    LocalDate.now(), LocalDate.now().plusYears(1)
            );
            when(prescriptionRepository.save(any(Prescription.class))).thenReturn(activePrescription);

            Prescription result = prescriptionService.createPrescription(command);

            assertThat(result).isNotNull();
            assertThat(result.getStatus()).isEqualTo(PrescriptionStatus.ACTIVE);
            assertThat(result.getPatientId()).isEqualTo("patient-001");
            verify(prescriptionRepository, times(1)).save(any(Prescription.class));
        }
    }

    @Nested
    @DisplayName("getPrescription")
    class GetPrescription {

        @Test
        @DisplayName("returns prescription when found")
        void getPrescription_returnsPrescriptionWhenFound() {
            UUID id = activePrescription.getId();
            when(prescriptionRepository.findById(id)).thenReturn(Optional.of(activePrescription));

            Prescription result = prescriptionService.getPrescription(id);

            assertThat(result).isEqualTo(activePrescription);
        }

        @Test
        @DisplayName("throws PrescriptionNotFoundException when not found")
        void getPrescription_throwsWhenNotFound() {
            UUID id = UUID.randomUUID();
            when(prescriptionRepository.findById(id)).thenReturn(Optional.empty());

            assertThatThrownBy(() -> prescriptionService.getPrescription(id))
                    .isInstanceOf(PrescriptionNotFoundException.class)
                    .hasMessageContaining(id.toString());
        }
    }

    @Nested
    @DisplayName("getPrescriptionsByPatient")
    class GetPrescriptionsByPatient {

        @Test
        @DisplayName("returns list of prescriptions for a patient")
        void getPrescriptionsByPatient_returnsList() {
            when(prescriptionRepository.findByPatientId("patient-001"))
                    .thenReturn(List.of(activePrescription));

            List<Prescription> results = prescriptionService.getPrescriptionsByPatient("patient-001");

            assertThat(results).hasSize(1).contains(activePrescription);
        }
    }

    @Nested
    @DisplayName("refillPrescription")
    class RefillPrescription {

        @Test
        @DisplayName("decrements refillsRemaining and saves")
        void refillPrescription_decrementsRefillsAndSaves() {
            UUID id = activePrescription.getId();
            when(prescriptionRepository.findById(id)).thenReturn(Optional.of(activePrescription));
            when(prescriptionRepository.save(any(Prescription.class))).thenReturn(activePrescription);

            prescriptionService.refillPrescription(id);

            assertThat(activePrescription.getRefillsRemaining()).isEqualTo(2);
            verify(prescriptionRepository).save(activePrescription);
        }

        @Test
        @DisplayName("throws IllegalStateException when no refills remain")
        void refillPrescription_throwsWhenNoRefillsRemain() {
            activePrescription.setRefillsRemaining(0);
            UUID id = activePrescription.getId();
            when(prescriptionRepository.findById(id)).thenReturn(Optional.of(activePrescription));

            assertThatThrownBy(() -> prescriptionService.refillPrescription(id))
                    .isInstanceOf(IllegalStateException.class);
        }
    }

    @Nested
    @DisplayName("cancelPrescription")
    class CancelPrescription {

        @Test
        @DisplayName("sets status to CANCELLED and saves")
        void cancelPrescription_setsStatusCancelledAndSaves() {
            UUID id = activePrescription.getId();
            when(prescriptionRepository.findById(id)).thenReturn(Optional.of(activePrescription));
            when(prescriptionRepository.save(any(Prescription.class))).thenReturn(activePrescription);

            prescriptionService.cancelPrescription(id);

            assertThat(activePrescription.getStatus()).isEqualTo(PrescriptionStatus.CANCELLED);
            verify(prescriptionRepository).save(activePrescription);
        }
    }
}
