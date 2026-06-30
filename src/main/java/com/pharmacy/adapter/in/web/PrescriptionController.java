package com.pharmacy.adapter.in.web;

import com.pharmacy.application.port.in.CreatePrescriptionCommand;
import com.pharmacy.application.port.in.PrescriptionUseCase;
import com.pharmacy.domain.model.Prescription;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

/**
 * REST adapter — exposes prescription endpoints.
 */
@RestController
@RequestMapping("/api/v1/prescriptions")
public class PrescriptionController {

    private final PrescriptionUseCase prescriptionUseCase;

    public PrescriptionController(PrescriptionUseCase prescriptionUseCase) {
        this.prescriptionUseCase = prescriptionUseCase;
    }

    @PostMapping
    public ResponseEntity<Prescription> createPrescription(
            @Valid @RequestBody CreatePrescriptionCommand command) {
        Prescription created = prescriptionUseCase.createPrescription(command);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    @GetMapping("/{id}")
    public ResponseEntity<Prescription> getPrescription(@PathVariable UUID id) {
        return ResponseEntity.ok(prescriptionUseCase.getPrescription(id));
    }

    @GetMapping
    public ResponseEntity<List<Prescription>> getPrescriptionsByPatient(
            @RequestParam String patientId) {
        return ResponseEntity.ok(prescriptionUseCase.getPrescriptionsByPatient(patientId));
    }

    @PostMapping("/{id}/refill")
    public ResponseEntity<Prescription> refillPrescription(@PathVariable UUID id) {
        return ResponseEntity.ok(prescriptionUseCase.refillPrescription(id));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> cancelPrescription(@PathVariable UUID id) {
        prescriptionUseCase.cancelPrescription(id);
        return ResponseEntity.noContent().build();
    }
}
