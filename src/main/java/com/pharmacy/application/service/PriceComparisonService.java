package com.pharmacy.application.service;

import com.pharmacy.application.port.in.PriceComparisonUseCase;
import com.pharmacy.application.port.out.MedicationPriceRepository;
import com.pharmacy.domain.model.MedicationPrice;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Comparator;
import java.util.List;

/**
 * Application service implementing price comparison use cases.
 */
@Service
@Transactional(readOnly = true)
public class PriceComparisonService implements PriceComparisonUseCase {

    private final MedicationPriceRepository medicationPriceRepository;

    public PriceComparisonService(MedicationPriceRepository medicationPriceRepository) {
        this.medicationPriceRepository = medicationPriceRepository;
    }

    @Override
    public List<MedicationPrice> comparePrices(String medicationName) {
        return medicationPriceRepository.findByMedicationName(medicationName);
    }

    @Override
    public MedicationPrice getCheapestOption(String medicationName) {
        return medicationPriceRepository.findByMedicationName(medicationName)
                .stream()
                .min(Comparator.comparing(MedicationPrice::getPrice))
                .orElseThrow(() -> new IllegalArgumentException(
                        "No price data found for medication: " + medicationName));
    }
}
