from enum import Enum, auto


PARTICLES = {
    "GAMMA": 22,
    "PION_PLUS": 211,
    "PION_MINUS": -211,
    "PION_0": 111,
    "KAON_0_LONG": 130,
    "KAON_PLUS": 321,
    "KAON_MINUS": -321,
    "KAON_0_SHORT": 310,
    "ETA": 221,
    "PROTON": 2212,
    "NEUTRON": 2112,
    "ANTI_PROTON": -2212,
    "ANTI_NEUTRON": -2112,
    "ELECTRON": -11,
    "POSITRON": 11,
    "NU_E": -12,
    "ANTI_NU_E": 12,
    "MUON_PLUS": -13,
    "MUON_MINUS": 13,
    "LAMBDA": 3122,
    "SIGMA_PLUS": 3222,
    "SIGMA_0": 3212,
    "SIGMA_MINUS": 3112,
    "XI_0": 3322,
    "XI_MINUS": 3312,
    "OMEGA_MINUS": 3334,
    "ANTI_LAMBDA": -3122,
    "ANTI_SIGMA_MINUS": -3222,
    "ANTI_SIGMA_0": -3212,
    "ANTI_SIGMA_PLUS": -3112,
    "ANTI_XI_0": -3322,
    "ANTI_XI_PLUS": -3312,
    "ANTI_OMEGA_PLUS": -3334,
    "TAU_PLUS": -15,
    "TAU_MINUS": 15,
    "D_PLUS": 441,
    "D_MINUS": -441,
    "D0": 421,
    "ANTI_D0": -421,
    "DS_PLUS": 431,
    "DS_MINUS": -431,
    "W_PLUS": 24,
    "W_MINUS": -24,
    "Z0": 23,
    "NU_M": -14,
    "ANTI_NU_M": 14,
    "NU_T": -16,
    "ANTI_NU_T": 16,
    "GEANT71": 71,
    "GEANT72": 72,
    "GEANT75": 75,
    "DEUTERON": 700201,
    "TRITON": 700301,
    "ALPHA": 700202,
    "HE3": 700302,
}


PARTICLE_IDS = {
    22: "GAMMA",
    211: "PION_PLUS",
    -211: "PION_MINUS",
    111: "PION_0",
    130: "KAON_0_LONG",
    321: "KAON_PLUS",
    -321: "KAON_MINUS",
    310: "KAON_0_SHORT",
    221: "ETA",
    2212: "PROTON",
    2112: "NEUTRON",
    -2212: "ANTI_PROTON",
    -2112: "ANTI_NEUTRON",
    -11: "ELECTRON",
    11: "POSITRON",
    -12: "NU_E",
    12: "ANTI_NU_E",
    -13: "MUON_PLUS",
    13: "MUON_MINUS",
    3122: "LAMBDA",
    3222: "SIGMA_PLUS",
    3212: "SIGMA_0",
    3112: "SIGMA_MINUS",
    3322: "XI_0",
    3312: "XI_MINUS",
    3334: "OMEGA_MINUS",
    -3122: "ANTI_LAMBDA",
    -3222: "ANTI_SIGMA_MINUS",
    -3212: "ANTI_SIGMA_0",
    -3112: "ANTI_SIGMA_PLUS",
    -3322: "ANTI_XI_0",
    -3312: "ANTI_XI_PLUS",
    -3334: "ANTI_OMEGA_PLUS",
    -15: "TAU_PLUS",
    15: "TAU_MINUS",
    441: "D_PLUS",
    -441: "D_MINUS",
    421: "D0",
    -421: "ANTI_D0",
    431: "DS_PLUS",
    -431: "DS_MINUS",
    24: "W_PLUS",
    -24: "W_MINUS",
    23: "Z0",
    -14: "NU_M",
    14: "ANTI_NU_M",
    -16: "NU_T",
    16: "ANTI_NU_T",
    71: "GEANT71",
    72: "GEANT72",
    75: "GEANT75",
    700201: "DEUTERON",
    700301: "TRITON",
    700202: "ALPHA",
    700302: "HE3",

}


class Particle(Enum):
    def _generate_next_value_(name, *args):
        return name

    GAMMA = auto()
    PION_PLUS = auto()
    PION_MINUS = auto()
    PION_0 = auto()
    KAON_0_LONG = auto()
    KAON_PLUS = auto()
    KAON_MINUS = auto()
    KAON_0_SHORT = auto()
    ETA = auto()
    PROTON = auto()
    NEUTRON = auto()
    ANTI_PROTON = auto()
    ANTI_NEUTRON = auto()
    ELECTRON = auto()
    POSITRON = auto()
    NU_E = auto()
    ANTI_NU_E = auto()
    MUON_PLUS = auto()
    MUON_MINUS = auto()
    LAMBDA = auto()
    SIGMA_PLUS = auto()
    SIGMA_0 = auto()
    SIGMA_MINUS = auto()
    XI_0 = auto()
    XI_MINUS = auto()
    OMEGA_MINUS = auto()
    ANTI_LAMBDA = auto()
    ANTI_SIGMA_MINUS = auto()
    ANTI_SIGMA_0 = auto()
    ANTI_SIGMA_PLUS = auto()
    ANTI_XI_0 = auto()
    ANTI_XI_PLUS = auto()
    ANTI_OMEGA_PLUS = auto()
    TAU_PLUS = auto()
    TAU_MINUS = auto()
    D_PLUS = auto()
    D_MINUS = auto()
    D0 = auto()
    ANTI_D0 = auto()
    DS_PLUS = auto()
    DS_MINUS = auto()
    W_PLUS = auto()
    W_MINUS = auto()
    Z0 = auto()
    NU_M = auto()
    ANTI_NU_M = auto()
    NU_T = auto()
    ANTI_NU_T = auto()
    GEANT71 = auto()
    GEANT72 = auto()
    GEANT75 = auto()
    DEUTERON = auto()
    TRITON = auto()
    ALPHA = auto()
    HE3 = auto()
