package com.pharmacy.adapter.in.web;

import com.pharmacy.application.port.in.PriceComparisonUseCase;
import com.pharmacy.domain.model.MedicationPrice;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * REST adapter — exposes price comparison endpoints.
 */
@RestController
@RequestMapping("/api/v1/prices")
public class PriceComparisonController {

    private final PriceComparisonUseCase priceComparisonUseCase;

    public PriceComparisonController(PriceComparisonUseCase priceComparisonUseCase) {
        this.priceComparisonUseCase = priceComparisonUseCase;
    }

    @GetMapping
    public ResponseEntity<List<MedicationPrice>> comparePrices(
            @RequestParam String medicationName) {
        return ResponseEntity.ok(priceComparisonUseCase.comparePrices(medicationName));
    }

    @GetMapping("/cheapest")
    public ResponseEntity<MedicationPrice> getCheapestOption(
            @RequestParam String medicationName) {
        return ResponseEntity.ok(priceComparisonUseCase.getCheapestOption(medicationName));
    }
}
