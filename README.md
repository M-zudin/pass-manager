# pass-manager
Python password manager, it looks like secure for some tasks

<h2>You will need to install these libraries:</h2>

pyAesCrypt

wmi

<h2>Features:</h2>

In-memoryAES-256 encryption/decryption (plaintext never will be on disk, only in RAM) for your passwords

File names are generated using SHA-256, so they don't tell anything about sites, but the same site+password will always give the same file name, that's why it works

<h3>Hardware key support</h3>

For this program, any internal disk may be a hardware key

That's how it works:

<ul>
  <li>A big random file created on disk, taking almost all space</li>
  <li>This file encrypted, using serial number of your disk C and serial number of hardware key</li>
  <li>Random byte chosen as "start byte"</li>
  <li>Its position encoded, making short and easy-to-remember password</li>
</ul>

After that, your 3FA is ready, and factors are serial number of hardware key, serial number of your disk C and password
