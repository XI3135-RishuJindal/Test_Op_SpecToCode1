package com.pharmacy.application.port.in;

import com.pharmacy.domain.model.MedicationPrice;

import java.util.List;

/**
 * Inbound port — price comparison use cases.
 */
public interface PriceComparisonUseCase {

    List<MedicationPrice> comparePrices(String medicationName);

    MedicationPrice getCheapestOption(String medicationName);
}
