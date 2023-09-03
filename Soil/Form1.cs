using System.Diagnostics;
using System.IO;
using System.Text.Json;
using System.Windows.Forms;

namespace Soil
{
    public partial class Form1 : Form
    {
        private int proxy_pid;
        public Form1()
        {
            InitializeComponent();
        }

        Settings settings = new Settings();
        string appPath = Path.GetDirectoryName(Application.ExecutablePath);
        private void button3_Click(object sender, EventArgs e)
        {
            string cjson = File.ReadAllText("config.json");
            string sourceFilePath = appPath + "/patch/mhypbase.dll";


            AppConfig config = JsonSerializer.Deserialize<AppConfig>(cjson);

            string destinationPath = config.game_folder;
            if (File.Exists(Path.GetDirectoryName(destinationPath) + "/mhypbase.dll"))
            {
                File.Move(Path.GetDirectoryName(destinationPath) + "/mhypbase.dll", appPath + "/patch/original/mhypbase.dll");
                File.Move(sourceFilePath, Path.GetDirectoryName(destinationPath) + "/mhypbase.dll");
                config.patched = true;

                string configtoWrite = JsonSerializer.Serialize(config, new JsonSerializerOptions
                {
                    WriteIndented = true // To make the JSON output more readable
                });

                string filePath = "config.json";


                try
                {
                    // Write the JSON content to the file
                    File.WriteAllText(filePath, configtoWrite);
                }
                catch (Exception ex)
                {
                    MessageBox.Show("Error: " + ex.Message);
                }
            }
            else
            {
                MessageBox.Show("mhypbase.dll not found. Patch has not been applied.", "Error");
            }
        }

        private void button2_Click(object sender, EventArgs e)
        {
            Settings settings = new Settings();
            settings.Show();
        }

        private void button4_Click(object sender, EventArgs e)
        {
            string cjson = File.ReadAllText("config.json");
            string sourceFilePath = appPath + "/patch/original/mhypbase.dll";


            AppConfig config = JsonSerializer.Deserialize<AppConfig>(cjson);

            string destinationPath = Path.GetDirectoryName(config.game_folder);
            if (File.Exists(destinationPath + "/mhypbase.dll"))
            {
                File.Move(destinationPath + "/mhypbase.dll", appPath + "/patch/mhypbase.dll");
                File.Move(sourceFilePath, destinationPath + "/mhypbase.dll");
                config.patched = false;

                string configtoWrite = JsonSerializer.Serialize(config, new JsonSerializerOptions
                {
                    WriteIndented = true // To make the JSON output more readable
                });

                string filePath = "config.json";


                try
                {
                    // Write the JSON content to the file
                    File.WriteAllText(filePath, configtoWrite);
                }
                catch (Exception ex)
                {
                    MessageBox.Show("Error: " + ex.Message);
                }
            }
            else
            {
                MessageBox.Show("mhypbase.dll not found.", "Error");
            }
        }

        private void checkBox1_CheckedChanged(object sender, EventArgs e)
        {
            if (checkBox1.Checked == true)
            {
                string json = File.ReadAllText("config.json");

                AppConfig config = JsonSerializer.Deserialize<AppConfig>(json);

                config.play_gc = true;

                string configtoWrite = JsonSerializer.Serialize(config, new JsonSerializerOptions
                {
                    WriteIndented = true // To make the JSON output more readable
                });

                string filePath = "config.json";

                try
                {
                    // Write the JSON content to the file
                    File.WriteAllText(filePath, configtoWrite);
                }
                catch (Exception ex)
                {
                    MessageBox.Show("Error: " + ex.Message);
                }
                string command = "cd " + Application.ExecutablePath + "/" + " && python3 proxy.py -ho " + textBox1 + ":" + textBox2;

                // Create a new process to run the command
                Process process = new Process
                {
                    StartInfo = new ProcessStartInfo
                    {
                        FileName = "/bin/bash", // Use the bash shell
                        RedirectStandardInput = true,
                        RedirectStandardOutput = true,
                        UseShellExecute = false,
                        CreateNoWindow = true,
                        RedirectStandardError = true
                    }
                };

                process.Start();

                // Send the command to the terminal
                process.StandardInput.WriteLine(command);

                if (checkBox1.Checked == false)
                {
                    process.Kill();
                }
            }
        }

        private void button1_Click(object sender, EventArgs e)
        {
            string cjson = File.ReadAllText("config.json");

            AppConfig config = JsonSerializer.Deserialize<AppConfig>(cjson);

            Process.Start(config.game_folder);
        }

        private void button5_Click(object sender, EventArgs e)
        {
            checkBox1.Checked = false;
            Thread.Sleep(2000);
            Application.Exit();
        }
    }
}