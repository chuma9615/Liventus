using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ConsoleApplication4
{
    class Program
    {
        static void Main(string[] args)
        {
            string comando = "E:/ScriptGraficosPython/main.py";
            string argumentos = args[0];
            string timestamp = args[1];
            string correo = args[2];
            //Console.WriteLine(argumentos);
            string resultado = run_cmd(comando, argumentos, timestamp);
            EnviarCorreo(timestamp,correo);

        }

        public static string
            run_cmd(string cmd, string args, string timestamp)
        {
            ProcessStartInfo start = new ProcessStartInfo();
            start.FileName = "C:/ProgramData/Anaconda3/envs/py34/python.exe";
            start.Arguments = string.Format("\"{0}\" \"{1}\" \"{2}\" ", cmd, args, timestamp);
            Console.WriteLine(start.Arguments);
            //Console.WriteLine(start.Arguments);
            start.UseShellExecute = false;// Do not use OS shell
            start.CreateNoWindow = true; // We don't need new window
            start.RedirectStandardOutput = true;// Any output, generated by application will be redirected back
            start.RedirectStandardError = true; // Any error in standard output will be redirected back (for example exceptions)
            using (Process process = Process.Start(start))
            {
                using (StreamReader reader = process.StandardOutput)
                {
                    string stderr = process.StandardError.ReadToEnd(); // Here are the exceptions from our Python script
                    string result = reader.ReadToEnd(); // Here is the result of StdOut(for example: print "test")
                    return result;
                }
            }
        }

        public static void EnviarCorreo(string timestamp, string maildestino)
        {

            string Correo = "";

            //Creamos un nuevo Objeto de mensaje
            System.Net.Mail.MailMessage mmsg = new System.Net.Mail.MailMessage();
            //Direccion de correo electronico a la que queremos enviar el mensaje
            mmsg.To.Add(maildestino);


            //Nota: La propiedad To es una colección que permite enviar el mensaje a más de un destinatario

            //Asunto de Alerta
            mmsg.Subject = "Graficos Servicio";

            mmsg.SubjectEncoding = System.Text.Encoding.UTF8;

            //Direccion de correo electronico que queremos que reciba una copia del mensaje
            // mmsg.Bcc.Add("randal.contreras.l@gmail.com"); //Opcional

            //Cuerpo del Mensaje Alerta
            string abspath = "E:/ScriptGraficosPython/Graficos" + "/" + timestamp;
            bool existe = File.Exists(abspath + ".zip");
            if (existe)
            {
                mmsg.Body = "<p>Estimad@ <p/>" +
                            "<p>Adjunto a este correo están los graficos solicitados </p>";

                mmsg.Attachments.Add(new System.Net.Mail.Attachment(abspath +  ".zip"));

            }
            else
            {
                mmsg.Body = "<p>Estimad@ <p/>" +
                                "<p>No se encontraron los graficos solicitados </p>";
            }
            mmsg.BodyEncoding = System.Text.Encoding.UTF8;
            mmsg.IsBodyHtml = true; //Si no queremos que se envíe como HTML

            //Correo electronico desde la que enviamos el mensaje
            mmsg.From = new System.Net.Mail.MailAddress("");


            /*-------------------------CLIENTE DE CORREO----------------------*/
            //Creamos un objeto de cliente de correo
            System.Net.Mail.SmtpClient cliente = new System.Net.Mail.SmtpClient();

            //Hay que crear las credenciales del correo emisor
            cliente.Credentials = new System.Net.NetworkCredential("", "");

            //Lo siguiente es obligatorio si enviamos el mensaje desde Gmail

            cliente.Port = 587;
            cliente.EnableSsl = true;


            //cliente.Host = "smtp.gmail.com"; //Para Gmail "smtp.gmail.com";
            cliente.Host = "outlook.office365.com";


            /*-------------------------ENVIO DE CORREO----------------------*/

            try
            {
                //Enviamos el mensaje
                cliente.Send(mmsg);
                mmsg.Dispose();
                if (existe)
                {
                    Directory.Delete(abspath, true);
                    File.Delete(abspath + ".zip");
                }



            }
            catch (System.Net.Mail.SmtpException ex)
            {

            }
        }
    }
}