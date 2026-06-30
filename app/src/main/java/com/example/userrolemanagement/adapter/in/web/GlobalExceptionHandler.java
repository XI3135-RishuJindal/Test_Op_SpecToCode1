package com.example.userrolemanagement.adapter.in.web;

import com.example.userrolemanagement.domain.exception.RoleAlreadyExistsException;
import com.example.userrolemanagement.domain.exception.RoleNotFoundException;
import com.example.userrolemanagement.domain.exception.UserRoleAlreadyAssignedException;
import com.example.userrolemanagement.domain.exception.UserRoleNotFoundException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ProblemDetail;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.util.stream.Collectors;

/**
 * Centralised exception-to-HTTP mapping for the REST adapter layer.
 */
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(RoleNotFoundException.class)
    public ProblemDetail handleRoleNotFound(RoleNotFoundException ex) {
        ProblemDetail pd = ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND, ex.getMessage());
        pd.setTitle("Role Not Found");
        return pd;
    }

    @ExceptionHandler(RoleAlreadyExistsException.class)
    public ProblemDetail handleRoleAlreadyExists(RoleAlreadyExistsException ex) {
        ProblemDetail pd = ProblemDetail.forStatusAndDetail(HttpStatus.CONFLICT, ex.getMessage());
        pd.setTitle("Role Already Exists");
        return pd;
    }

    @ExceptionHandler(UserRoleAlreadyAssignedException.class)
    public ProblemDetail handleUserRoleAlreadyAssigned(UserRoleAlreadyAssignedException ex) {
        ProblemDetail pd = ProblemDetail.forStatusAndDetail(HttpStatus.CONFLICT, ex.getMessage());
        pd.setTitle("Role Already Assigned");
        return pd;
    }

    @ExceptionHandler(UserRoleNotFoundException.class)
    public ProblemDetail handleUserRoleNotFound(UserRoleNotFoundException ex) {
        ProblemDetail pd = ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND, ex.getMessage());
        pd.setTitle("User Role Assignment Not Found");
        return pd;
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ProblemDetail handleValidation(MethodArgumentNotValidException ex) {
        String detail = ex.getBindingResult().getFieldErrors().stream()
                .map(fe -> fe.getField() + ": " + fe.getDefaultMessage())
                .collect(Collectors.joining("; "));
        ProblemDetail pd = ProblemDetail.forStatusAndDetail(HttpStatus.BAD_REQUEST, detail);
        pd.setTitle("Validation Failed");
        return pd;
    }
}
