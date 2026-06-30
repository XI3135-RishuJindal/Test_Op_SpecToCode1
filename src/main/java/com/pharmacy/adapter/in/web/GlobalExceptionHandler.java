package com.pharmacy.adapter.in.web;

import com.pharmacy.domain.exception.AdherenceRecordNotFoundException;
import com.pharmacy.domain.exception.PrescriptionNotFoundException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ProblemDetail;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.net.URI;

/**
 * Global exception handler — maps domain exceptions to HTTP responses.
 */
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(PrescriptionNotFoundException.class)
    public ProblemDetail handlePrescriptionNotFound(PrescriptionNotFoundException ex) {
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND, ex.getMessage());
        problem.setType(URI.create("https://pharmacy.example.com/errors/prescription-not-found"));
        return problem;
    }

    @ExceptionHandler(AdherenceRecordNotFoundException.class)
    public ProblemDetail handleAdherenceNotFound(AdherenceRecordNotFoundException ex) {
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND, ex.getMessage());
        problem.setType(URI.create("https://pharmacy.example.com/errors/adherence-not-found"));
        return problem;
    }

    @ExceptionHandler(IllegalArgumentException.class)
    public ProblemDetail handleIllegalArgument(IllegalArgumentException ex) {
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(HttpStatus.BAD_REQUEST, ex.getMessage());
        problem.setType(URI.create("https://pharmacy.example.com/errors/bad-request"));
        return problem;
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ProblemDetail handleValidation(MethodArgumentNotValidException ex) {
        String detail = ex.getBindingResult().getFieldErrors().stream()
                .map(fe -> fe.getField() + ": " + fe.getDefaultMessage())
                .reduce((a, b) -> a + "; " + b)
                .orElse("Validation failed");
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(HttpStatus.BAD_REQUEST, detail);
        problem.setType(URI.create("https://pharmacy.example.com/errors/validation-error"));
        return problem;
    }
}
