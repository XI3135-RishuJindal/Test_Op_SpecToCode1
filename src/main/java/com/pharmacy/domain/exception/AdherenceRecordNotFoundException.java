package com.pharmacy.domain.exception;

public class AdherenceRecordNotFoundException extends RuntimeException {

    public AdherenceRecordNotFoundException(java.util.UUID id) {
        super("Adherence record not found with id: " + id);
    }
}
