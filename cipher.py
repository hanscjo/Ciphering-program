import random
import crypto_utils


class Cipher():

    _alphabet_length = 95

    def encode(self, text, key):
        encoded_text = 0
        return encoded_text

    def decode(self, text, key):
        decoded_text = 0
        return decoded_text

    def verify(self, text, key1, key2):
        test_text = self.encode(text, key1)
        test_text = self.decode(test_text, key2)

        return text == test_text

    def generate_keys(self, sender, receiver):
        sender.set_key(random.randint(0, self._alphabet_length))
        receiver.set_key(random.randint(0, self._alphabet_length))

class Person():


    def set_key(self, key):
        self._key = key

    def get_key(self):
        return self._key

    def operate_cipher(self, text):
        text = self._cipher.encode(text, self._key)
        text = self._cipher.decode(text, self._key)
        return text

class Sender(Person):

    def __init__(self, cipher):
        self._cipher = cipher
        self._key = 0

    def operate_cipher(self, text):
        return self._cipher.encode(text, self._key)


class Receiver(Person):

    def __init__(self, cipher):
        self._cipher = cipher
        self._key = 0

    def operate_cipher(self, text):
        return self._cipher.decode(text, self._key)


class Caesar(Cipher):

    def encode(self, text, key):
        text_letters = []
        encoded_text = ''

        for i in text:
            text_letters.append(ord(i)-31)

        for j in range(0, len(text_letters)):
            text_letters[j] = ((text_letters[j] + key) % (self._alphabet_length))+31

        for k in text_letters:
            encoded_text = encoded_text + chr(k)

        return encoded_text


    def decode(self, text, key):
        decoded_text = self.encode(text, key)
        return decoded_text

    def verify(self, text, key):
        test_text = self.encode(text, key)
        print(test_text)
        test_text = self.decode(test_text, self._alphabet_length - key)
        print(test_text)
        return text == test_text

    def generate_keys(self, sender, receiver):
        sender.set_key(random.randint(1, self._alphabet_length))
        receiver.set_key(self._alphabet_length - sender._key)


class Multiplicative(Cipher):

    def encode(self, text, key):
        text_letters = []
        encoded_text = ''

        for i in text:
            text_letters.append(ord(i)-31)

        for j in range(0, len(text_letters)):
            text_letters[j] = ((text_letters[j] * key) % self._alphabet_length)+31

        for k in text_letters:
            encoded_text = encoded_text + chr(k)

        return encoded_text

    def decode(self, text, key):
        decoded_text = self.encode(text, key)
        return decoded_text

    def verify(self, text, key):
        test_text = self.encode(text, key)
        print(test_text)
        test_text = self.decode(test_text, crypto_utils.modular_inverse(key, self._alphabet_length))
        print(test_text)

        return text == test_text

    def generate_keys(self, sender, receiver):
        sender_key = 0
        receiver_key = 0

        while receiver_key == 0:
            sender_key = random.randint(1, self._alphabet_length)
            receiver_key = crypto_utils.modular_inverse(sender_key, self._alphabet_length)

        sender.set_key(sender_key)
        receiver.set_key(receiver_key)


class Affine(Cipher):

    def encode(self, text, key):
        encoded_text = Multiplicative.encode(self, text, key[0])
        encoded_text = Caesar.encode(self, encoded_text, key[1])
        return encoded_text

    def decode(self, text, key):
        decoded_text = Caesar.encode(self, text, key[1])
        decoded_text = Multiplicative.encode(self, decoded_text, key[0])
        return decoded_text

    def verify(self, text, key):
        test_text = self.encode(text, key)
        print(test_text)
        key = (crypto_utils.modular_inverse(key[0], self._alphabet_length), self._alphabet_length - key[1])
        print(key)
        test_text = self.decode(test_text, key)
        print(test_text)

        return text == test_text

    def generate_keys(self, sender, receiver):
        sender_key_mul = 0
        receiver_key_mul = 0

        while receiver_key_mul == 0:
            sender_key_mul = random.randint(1, self._alphabet_length)
            receiver_key_mul = crypto_utils.modular_inverse(sender_key_mul, self._alphabet_length)

        sender_key_cae = random.randint(1, self._alphabet_length)
        receiver_key_cae = self._alphabet_length - sender_key_cae


        sender.set_key((sender_key_mul, sender_key_cae))
        receiver.set_key((receiver_key_mul, receiver_key_cae))


class Unbreakable(Cipher):

    def encode(self, text, key):
        text_letters = []
        encoded_text = ''

        for i in text:
            text_letters.append(ord(i)-31)

        for j in range(0, len(text_letters)):
            text_letters[j] = ((text_letters[j] + ord(key[j % len(key)])) % self._alphabet_length)+31

        for k in text_letters:
            encoded_text = encoded_text + chr(k)

        return encoded_text

    def decode(self, text, key):
        decoded_text = self.encode(text, key)
        return decoded_text

    def verify(self, text, key):
        test_text = self.encode(text, key)

        old_key = []
        new_key = []
        for i in range(0, len(key)):
            old_key.append(ord(key[i]))
            new_key.append((self._alphabet_length - old_key[i]) % self._alphabet_length)

        key = ''

        for j in new_key:
            key = key + chr(j)
        print(key)
        test_text = self.decode(test_text, key)

        return text == test_text

    def generate_keys(self, sender, receiver, key_length):
        sender_set = []
        receiver_set = []

        for i in range(0, key_length):
            sender_set.append(random.randint(1+31, self._alphabet_length)+31)
            receiver_set.append((self._alphabet_length - sender_set[i]) % self._alphabet_length)

        sender_key = ''
        receiver_key = ''

        for j in range(0, key_length):
            sender_key = sender_key + chr(sender_set[j])
            receiver_key = receiver_key + chr(receiver_set[j])

        sender.set_key(sender_key)
        receiver.set_key(receiver_key)


class Hacker(Person):
    _simplemax = 95
    _affinemax = 95*95

    def __init__(self, cipher):
        self._cipher = cipher
        self._key = 0

    def operate_cipher(self, text):
        _found = False

        if type(self._cipher) == Caesar or type(self._cipher) == Multiplicative:
            print("Simple cipher")
            i = 1
            while (i < self._simplemax) and (not _found):
                    orig_text = self._cipher.decode(text, i)

                    orig_text_muted = orig_text.replace(',', '')
                    orig_text_muted = orig_text_muted.replace('.', '')

                    orig_text_array = orig_text_muted.split()

                    f = open("english_words.txt", "r")
                    for j in f:
                        j = j.replace('\n', '')
                        if j in orig_text_array:
                            print(j, "ble funnet som ord i den originale teksten")
                            _found = True

                    f.close()
                    i += 1

            if _found:
                print("Nøkkelen var:", i-1, "og teksten var:", orig_text)
            else:
                print("Fant ingen match")


        elif type(self._cipher) == Affine:
            print("Affine cipher")
            i = 1
            h = 1
            forsøk = 0
            while (i < self._simplemax) and (not _found):
                h = 1
                while (h < self._simplemax) and (not _found):
                    orig_text = self._cipher.decode(text, (i, h))

                    orig_text_muted = orig_text.replace(',', '')
                    orig_text_muted = orig_text_muted.replace('.', '')

                    orig_text_array = orig_text_muted.split()

                    f = open("english_words.txt", "r")
                    for j in f:
                        j = j.replace('\n', '')
                        if j in orig_text_array:
                            print(j, "ble funnet som ord i den originale teksten")
                            _found = True

                    f.close()
                    h += 1
                    forsøk += 1
                i += 1
            if _found:
                print("Nøkkelen var:", (i-1, h-1), "og teksten var:", orig_text, "søket tok", forsøk, "forsøk")
            else:
                print("Fant ingen match")

        elif type(self._cipher) == Unbreakable:
            print("Unbreakable cipher")
            words = []
            f = open("english_words.txt", "r")
            for i in f:
                words.append(i.replace('\n', ''))
            f.close()

            l = 0
            while (l < len(words)) and (not _found):
                    print(words[l])
                    words[l]
                    orig_text = self._cipher.decode(text, words[l])

                    orig_text_muted = orig_text.replace(',', '')
                    orig_text_muted = orig_text_muted.replace('.', '')

                    orig_text_array = orig_text_muted.split()

                    f = open("english_words.txt", "r")
                    for j in f:
                        j = j.replace('\n', '')
                        if j in orig_text_array:
                            print(orig_text_array)
                            print(j, "ble funnet som ord i den originale teksten")
                            _found = True
                    f.close()
                    l += 1


            if _found:
                print("Nøkkelen var:", words[l-1], "og teksten var:", orig_text)
            else:
                print("Fant ingen match")

        else:
            print("No recognized cipher")
