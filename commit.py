import random
from ZeroKnowledge import bbs

class CommitmentScheme(object):
    def __init__(self, oneWayPermutation, hardcorePredicate, securityParameter):
        '''
            oneWayPermutation: int -> int
            hardcorePredicate: int -> {0, 1}
        '''
        self.oneWayPermutation = oneWayPermutation
        self.hardcorePredicate = hardcorePredicate
        self.securityParameter = securityParameter

        # a random string of length `self.securityParameter` used only once per commitment
        self.secret = self.generateSecret()

    def generateSecret(self):
        raise NotImplemented

    def commit(self, x):
        print('commit Place 1')
        raise NotImplemented

    def reveal(self):
        return self.secret

class BBSBitCommitmentScheme(CommitmentScheme):
    def generateSecret(self):
        # the secret is a random quadratic residue
        self.secret = self.oneWayPermutation(random.getrandbits(self.securityParameter))
        return self.secret

    def commit(self, bit):
        print('commit PLACE 2')
        unguessableBit = self.hardcorePredicate(self.secret)
        return (
            self.oneWayPermutation(self.secret),
            unguessableBit ^ bit,  # python xor
        )

class BBSBitCommitmentVerifier(object):
    def __init__(self, oneWayPermutation, hardcorePredicate):
        self.oneWayPermutation = oneWayPermutation
        self.hardcorePredicate = hardcorePredicate

    def verify(self, securityString, claimedCommitment):
        trueBit = self.decode(securityString, claimedCommitment)
        unguessableBit = self.hardcorePredicate(securityString)  # wasteful, whatever
        return claimedCommitment == (
            self.oneWayPermutation(securityString),
            unguessableBit ^ trueBit,  # python xor
        )

    def decode(self, securityString, claimedCommitment):
        unguessableBit = self.hardcorePredicate(securityString)
        return claimedCommitment[1] ^ unguessableBit

class BBSStringCommitmentScheme(CommitmentScheme):
    def __init__(self, numBits, oneWayPermutation, hardcorePredicate, securityParameter=512):
        '''
            A commitment scheme for integers of a prespecified length `numBits`. Applies the
            bit commitment scheme to each bit independently.
        '''
        self.schemes = [BBSBitCommitmentScheme(oneWayPermutation, hardcorePredicate, securityParameter)
                        for _ in range(numBits)]
        super().__init__(oneWayPermutation, hardcorePredicate, securityParameter)

    def generateSecret(self):
        self.secret = [x.secret for x in self.schemes]
        return self.secret

    def commit(self, data):
        print('commit PLACE 3: data len: ', len(data))
        binaryString = ""
        for ch in str(data):
            chInBin = format(ord(ch), 'b').zfill(8)
            binaryString += str(chInBin)
        bits = [int(char) for char in binaryString]
        return [scheme.commit(bit) for scheme, bit in zip(self.schemes, bits)]

class BBSStringCommitmentVerifier(object):
    def __init__(self, numBits, oneWayPermutation, hardcorePredicate):
        self.verifiers = [BBSBitCommitmentVerifier(oneWayPermutation, hardcorePredicate)
                          for _ in range(numBits)]

    def decodeBits(self, secrets, bitCommitments):
        return [v.decode(secret, commitment) for (v, secret, commitment) in
                zip(self.verifiers, secrets, bitCommitments)]

    def verify(self, secrets, bitCommitments):
        return all(
            bitVerifier.verify(secret, commitment)
            for (bitVerifier, secret, commitment) in
            zip(self.verifiers, secrets, bitCommitments)
        )

    def decode(self, secrets, bitCommitments):
        decodedBits = self.decodeBits(secrets, bitCommitments)
        binary = ''.join(str(bit) for bit in decodedBits)
        n = 8;
        binarySets = [binary[i:i+n] for i in range(0, len(binary), n)]
        chars  = [chr(int(charBin, 2)) for charBin in binarySets]
        return ''.join(chars)

if __name__ == "__main__":

    securityParameter = 10
    oneWayPerm = bbs.bbs(securityParameter)
    hardcorePred = bbs.parity
    scheme = BBSStringCommitmentScheme(512, oneWayPerm, hardcorePred)
    verifier = BBSStringCommitmentVerifier(512, oneWayPerm, hardcorePred)

    data = {
    "fruits":[
        "apple",
        "banana"
        ]
    }

    data = str(data)

    tc = ["hello", data]

    for string in tc:

        commitments = scheme.commit(string)
        secrets = scheme.reveal()
        trueString = verifier.decode(secrets, commitments)
        valid = verifier.verify(secrets, commitments)

        print(f"INPUT STRING : {string}")
        print(f"DECODED STRING : {trueString}")
        print(f"VALIDATION : {valid}")
        print(f"SECRET : {secrets}")
        print(f"COMMITMENTS : {commitments}")
        print("\n\n")
