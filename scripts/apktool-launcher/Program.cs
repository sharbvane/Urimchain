using System;
using System.Diagnostics;
using System.IO;
using System.Text.Json;

var root = Directory.GetParent(AppContext.BaseDirectory.TrimEnd(Path.DirectorySeparatorChar))!.FullName;
using var config = JsonDocument.Parse(File.ReadAllText(Path.Combine(root, "toolchain.json")));
var command = new ProcessStartInfo(Path.Combine(config.RootElement.GetProperty("jdk").GetString()!, "bin", "java.exe")) { UseShellExecute = false };
command.ArgumentList.Add("-jar");
command.ArgumentList.Add(config.RootElement.GetProperty("apktool").GetString()!);
foreach (var argument in args) command.ArgumentList.Add(argument);
using var process = Process.Start(command) ?? throw new InvalidOperationException("Cannot start Java");
process.WaitForExit();
return process.ExitCode;
