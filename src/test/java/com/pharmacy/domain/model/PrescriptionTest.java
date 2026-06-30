package com.pharmacy.domain.model;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

import java.time.LocalDate;
import java.util.UUID;

import static org.assertj.core.api.Assertions.*;

/**
 * Unit tests for the Prescription domain entity.
 */
@DisplayName("Prescription")
class PrescriptionTest {

    private Prescription buildPrescription(int refillsRemaining, LocalDate expiryDate,
                                           PrescriptionStatus status) {
        return new Prescription(
                UUID.randomUUID(),
                "patient-001",
                "Metformin",
                "500mg",
                90,
                refillsRemaining,
                LocalDate.now(),
                expiryDate,
                status
        );
    }

    @Nested
    @DisplayName("isExpired")
    class IsExpired {

        @Test
        @DisplayName("returns false when expiry date is in the future")
        void isExpired_returnsFalseWhenFuture() {
            Prescription p = buildPrescription(2, LocalDate.now().plusDays(30), PrescriptionStatus.ACTIVE);
            assertThat(p.isExpired()).isFalse();
        }

        @Test
        @DisplayName("returns true when expiry date is in the past")
        void isExpired_returnsTrueWhenPast() {
            Prescription p = buildPrescription(2, LocalDate.now().minusDays(1), PrescriptionStatus.ACTIVE);
            assertThat(p.isExpired()).isTrue();
        }
    }

    @Nested
    @DisplayName("canRefill")
    class CanRefill {

        @Test
        @DisplayName("returns true when active, not expired, and refills remain")
        void canRefill_returnsTrueWhenEligible() {
            Prescription p = buildPrescription(2, LocalDate.now().plusDays(30), PrescriptionStatus.ACTIVE);
            assertThat(p.canRefill()).isTrue();
        }

        @Test
        @DisplayName("returns false when no refills remain")
        void canRefill_returnsFalseWhenNoRefills() {
            Prescription p = buildPrescription(0, LocalDate.now().plusDays(30), PrescriptionStatus.ACTIVE);
            assertThat(p.canRefill()).isFalse();
        }

        @Test
        @DisplayName("returns false when prescription is expired")
        void canRefill_returnsFalseWhenExpired() {
            Prescription p = buildPrescription(2, LocalDate.now().minusDays(1), PrescriptionStatus.ACTIVE);
            assertThat(p.canRefill()).isFalse();
        }

        @Test
        @DisplayName("returns false when prescription is cancelled")
        void canRefill_returnsFalseWhenCancelled() {
            Prescription p = buildPrescription(2, LocalDate.now().plusDays(30), PrescriptionStatus.CANCELLED);
            assertThat(p.canRefill()).isFalse();
        }
    }

    @Nested
    @DisplayName("refill")
    class Refill {

        @Test
        @DisplayName("decrements refillsRemaining by 1")
        void refill_decrementsRefillsRemaining() {
            Prescription p = buildPrescription(3, LocalDate.now().plusDays(30), PrescriptionStatus.ACTIVE);
            p.refill();
            assertThat(p.getRefillsRemaining()).isEqualTo(2);
        }

        @Test
        @DisplayName("throws IllegalStateException when cannot refill")
        void refill_throwsWhenCannotRefill() {
            Prescription p = buildPrescription(0, LocalDate.now().plusDays(30), PrescriptionStatus.ACTIVE);
            assertThatThrownBy(p::refill).isInstanceOf(IllegalStateException.class);
        }
    }

    @Nested
    @DisplayName("cancel")
    class Cancel {

        @Test
        @DisplayName("sets status to CANCELLED")
        void cancel_setsStatusCancelled() {
            Prescription p = buildPrescription(2, LocalDate.now().plusDays(30), PrescriptionStatus.ACTIVE);
            p.cancel();
            assertThat(p.getStatus()).isEqualTo(PrescriptionStatus.CANCELLED);
        }
    }
}
