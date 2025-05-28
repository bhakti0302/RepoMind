package com.example.incidents.service;

import org.springframework.stereotype.Service;
import com.sap.cds.services.handler.annotations.After;
import com.sap.cds.services.handler.annotations.Before;
import com.sap.cds.services.cds.CdsService;
import com.sap.cds.services.handler.annotations.On;
import com.sap.cds.services.handler.annotations.ServiceName;
import com.sap.cds.services.handler.EventHandler;
import cds.gen.*;
import java.util.ArrayList;
import java.util.List;

@Service
@ServiceName("ProperIncident")
public class ProperIncidentService implements EventHandler {
    
    public void processIncident(String incidentId) {
        System.out.println("Processing incident: " + incidentId);
        
        // Validate incident
        boolean isValid = validateIncident(incidentId);
        
        if (isValid) {
            System.out.println("Incident is valid");
        } else {
            System.out.println("Incident is invalid");
        }
    }
    
    private boolean validateIncident(String incidentId) {
        return incidentId != null && !incidentId.isEmpty();
    }
    
    public List<String> getAllIncidents() {
        return new ArrayList<>();
    }
} 