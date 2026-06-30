package com.pharmacy.adapter.in.web;

import com.pharmacy.application.port.in.AdherenceUseCase;
import com.pharmacy.application.port.in.RecordAdherenceCommand;
import com.pharmacy.domain.model.AdherenceRecord;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

/**
 * REST adapter — exposes medication adherence endpoints.
 */
@RestController
@RequestMapping("/api/v1/adherence")
public class AdherenceController {

    private final AdherenceUseCase adherenceUseCase;

    public AdherenceController(AdherenceUseCase adherenceUseCase) {
        this.adherenceUseCase = adherenceUseCase;
    }

    @PostMapping
    public ResponseEntity<AdherenceRecord> recordAdherence(
            @Valid @RequestBody RecordAdherenceCommand command) {
        AdherenceRecord record = adherenceUseCase.recordAdherence(command);
        return ResponseEntity.status(HttpStatus.CREATED).body(record);
    }

    @PatchMapping("/{id}/taken")
    public ResponseEntity<AdherenceRecord> markAsTaken(
            @PathVariable UUID id,
            @RequestParam(required = false) LocalDateTime takenAt) {
        LocalDateTime effectiveTakenAt = takenAt != null ? takenAt : LocalDateTime.now();
        return ResponseEntity.ok(adherenceUseCase.markAsTaken(id, effectiveTakenAt));
    }

    @GetMapping
    public ResponseEntity<List<AdherenceRecord>> getAdherenceByPatient(
            @RequestParam String patientId) {
        return ResponseEntity.ok(adherenceUseCase.getAdherenceByPatient(patientId));
    }

    @GetMapping("/rate")
    public ResponseEntity<Double> getAdherenceRate(@RequestParam String patientId) {
        return ResponseEntity.ok(adherenceUseCase.calculateAdherenceRate(patientId));
    }
}
