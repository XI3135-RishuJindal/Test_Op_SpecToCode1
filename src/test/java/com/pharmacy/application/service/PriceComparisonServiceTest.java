package com.pharmacy.application.service;

import com.pharmacy.application.port.out.MedicationPriceRepository;
import com.pharmacy.domain.model.MedicationPrice;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.math.BigDecimal;
import java.util.List;
import java.util.UUID;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.Mockito.*;

/**
 * Unit tests for PriceComparisonService.
 */
@ExtendWith(MockitoExtension.class)
@DisplayName("PriceComparisonService")
class PriceComparisonServiceTest {

    @Mock
    private MedicationPriceRepository medicationPriceRepository;

    @InjectMocks
    private PriceComparisonService priceComparisonService;

    private final List<MedicationPrice> samplePrices = List.of(
            new MedicationPrice(UUID.randomUUID(), "Ibuprofen", "PharmacyA", "Loc A",
                    new BigDecimal("12.99"), "USD"),
            new MedicationPrice(UUID.randomUUID(), "Ibuprofen", "PharmacyB", "Loc B",
                    new BigDecimal("9.49"), "USD"),
            new MedicationPrice(UUID.randomUUID(), "Ibuprofen", "PharmacyC", "Loc C",
                    new BigDecimal("14.00"), "USD")
    );

    @Nested
    @DisplayName("comparePrices")
    class ComparePrices {

        @Test
        @DisplayName("returns all prices for a medication")
        void comparePrices_returnsAllPrices() {
            when(medicationPriceRepository.findByMedicationName("Ibuprofen"))
                    .thenReturn(samplePrices);

            List<MedicationPrice> result = priceComparisonService.comparePrices("Ibuprofen");

            assertThat(result).hasSize(3);
        }
    }

    @Nested
    @DisplayName("getCheapestOption")
    class GetCheapestOption {

        @Test
        @DisplayName("returns the medication with the lowest price")
        void getCheapestOption_returnsCheapest() {
            when(medicationPriceRepository.findByMedicationName("Ibuprofen"))
                    .thenReturn(samplePrices);

            MedicationPrice cheapest = priceComparisonService.getCheapestOption("Ibuprofen");

            assertThat(cheapest.getPrice()).isEqualByComparingTo(new BigDecimal("9.49"));
            assertThat(cheapest.getPharmacyName()).isEqualTo("PharmacyB");
        }

        @Test
        @DisplayName("throws IllegalArgumentException when no prices found")
        void getCheapestOption_throwsWhenNoPricesFound() {
            when(medicationPriceRepository.findByMedicationName("UnknownDrug"))
                    .thenReturn(List.of());

            assertThatThrownBy(() -> priceComparisonService.getCheapestOption("UnknownDrug"))
                    .isInstanceOf(IllegalArgumentException.class)
                    .hasMessageContaining("UnknownDrug");
        }
    }
}
