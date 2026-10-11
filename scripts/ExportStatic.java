import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.DecompInterface;
import ghidra.program.model.listing.*;
import java.io.*;

public class ExportStatic extends GhidraScript {
    public void run() throws Exception {
        DecompInterface decompiler = new DecompInterface();
        decompiler.openProgram(currentProgram);
        try (PrintWriter output = new PrintWriter(new File(getScriptArgs()[0]), "UTF-8")) {
            FunctionIterator functions = currentProgram.getFunctionManager().getFunctions(true);
            int count = 0;
            // shortcut: exports at most 200 functions, use focused analysis for larger samples.
            while (functions.hasNext() && count++ < 200 && !monitor.isCancelled()) {
                Function f = functions.next();
                output.println("FUNCTION " + f.getName() + " @ " + f.getEntryPoint());
                InstructionIterator instructions = currentProgram.getListing().getInstructions(f.getBody(), true);
                while (instructions.hasNext()) output.println(instructions.next());
                var result = decompiler.decompileFunction(f, 30, monitor);
                if (result.decompileCompleted()) output.println(result.getDecompiledFunction().getC());
                else output.println("DECOMPILATION UNAVAILABLE: " + result.getErrorMessage());
            }
        } finally { decompiler.dispose(); }
    }
}
