using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Security.Cryptography.X509Certificates;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.IO;
using System.Text.Json;
using System.Net.Http.Json;

namespace Soil
{
    public partial class Settings : Form
    {
        public Settings()
        {
            InitializeComponent();
        }

        public string gameExec = "";

        private void button1_Click(object sender, EventArgs e)
        {
            OpenFileDialog openFileDialog1 = new OpenFileDialog();
            openFileDialog1.Title = "Select Game Executable";
            openFileDialog1.InitialDirectory = "~";
            openFileDialog1.Filter = "All files (*.*)|*.*";
            openFileDialog1.FilterIndex = 0;
            openFileDialog1.Multiselect = false;
            openFileDialog1.ShowDialog();
            if (openFileDialog1.FileName != "")
            {
                textBox1.Text = openFileDialog1.FileName;
                string json = File.ReadAllText("config.json");

                AppConfig config = JsonSerializer.Deserialize<AppConfig>(json);

                config.game_folder = openFileDialog1.FileName;

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
                textBox1.Text = "ERROR (FILE HAS AN EMPTY NAME)";
            }
        }

        private void Settings_Load(object sender, EventArgs e)
        {
            string json = File.ReadAllText("config.json");

            AppConfig config = JsonSerializer.Deserialize<AppConfig>(json);

            textBox1.Text = config.game_folder;
            if (config.patched == false)
            {
                label2.Text = "not applied";
                label2.ForeColor = Color.Red;
            } else if (config.patched == true) {
                label2.Text = "applied";
                label2.ForeColor = Color.Green;
            } else
            {
                label2.Text = "unknown, report this to (DISCORD) omegapobreton";
                label2.ForeColor = Color.Gray;
            }
        }
    }
}
