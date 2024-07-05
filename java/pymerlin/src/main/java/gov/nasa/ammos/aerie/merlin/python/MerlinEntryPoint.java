package gov.nasa.ammos.aerie.merlin.python;

import py4j.GatewayServer;

import java.util.ArrayList;
import java.util.List;

public class MerlinEntryPoint {
    private final Merlin merlin;

    public MerlinEntryPoint() {
        merlin = new Merlin();
    }

    public Merlin getMerlin() {
        return merlin;
    }

    public <T> List<T> getList() {
        return new ArrayList<>();
    }

    public <T> int take(T object) {
        return 0;
    }

    public static void main(String[] args) {
        GatewayServer gatewayServer = new GatewayServer(new MerlinEntryPoint());
        gatewayServer.start();
    }
}
