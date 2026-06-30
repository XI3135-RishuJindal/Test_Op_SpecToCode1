package com.pharmacy.application.port.out;

import com.pharmacy.domain.model.MedicationPrice;

import java.util.List;

/**
 * Outbound port — external price data source contract.
 */
public interface MedicationPriceRepository {

    List<MedicationPrice> findByMedicationName(String medicationName);
}
