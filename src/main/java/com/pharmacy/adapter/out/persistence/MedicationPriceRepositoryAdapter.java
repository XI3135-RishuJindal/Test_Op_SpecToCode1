package com.pharmacy.adapter.out.persistence;

import com.pharmacy.application.port.out.MedicationPriceRepository;
import com.pharmacy.domain.model.MedicationPrice;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.util.List;
import java.util.UUID;

/**
 * Stub outbound adapter for medication price data.
 * TODO: Replace with a real external API or database-backed implementation.
 */
@Component
public class MedicationPriceRepositoryAdapter implements MedicationPriceRepository {

    @Override
    public List<MedicationPrice> findByMedicationName(String medicationName) {
        // TODO: Integrate with a real pricing data source (e.g., external API or DB table)
        return List.of(
                new MedicationPrice(UUID.randomUUID(), medicationName, "PharmacyA", "Location A",
                        new BigDecimal("12.99"), "USD"),
                new MedicationPrice(UUID.randomUUID(), medicationName, "PharmacyB", "Location B",
                        new BigDecimal("10.49"), "USD"),
                new MedicationPrice(UUID.randomUUID(), medicationName, "PharmacyC", "Location C",
                        new BigDecimal("14.00"), "USD")
        );
    }
}
