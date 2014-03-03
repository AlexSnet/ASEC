import logging


class Registers:
    def __init__(self):
        # General registers, 8-bit
        self.a = 0  # Accumulation Register
        self.b = 0
        self.c = 0
        self.d = 0
        self.e = 0
        self.h = 0
        self.l = 0
        self.f = 0  # Flag register, 8-bit

        # Stack pointer, 16-bit
        self.sp = 0  #

        # Instruction pointer, 16-bit
        self.pc = 0  # Start execution at 0
        self.i = 0
        self.r = 0

        self.m = 0

        self.ime = 0

    def reset(self):
        self.a = 0
        self.b = 0
        self.c = 0
        self.d = 0
        self.e = 0
        self.h = 0
        self.l = 0
        self.f = 0
        self.sp = 0
        self.pc = 0
        self.i = 0
        self.r = 0
        self.m = 0
        self.ime = 0


class Clock:
    def __init__(self):
        self.m = 0

    def reset(self):
        self.m = 0


class Processor:
    def __init__(self, mainboard):
        self.mainboard = mainboard

        self.log = logging.getLogger(self.__class__.__name__)

        self._HALT = None
        self._STOP = None

        self.R = Registers()
        self.RSV = Registers()

        self.CLOCK = Clock()

        self.reset()
        
        self._map = [ #dict(( (i,x) for i,x in enumerate([
            # 00
            self.NOP, self.LDBCnn, self.LDBCmA, self.INCBC,
            self.INCr_b, self.DECr_b, self.LDrn_b, self.RLCA,
            self.LDmmSP, self.ADDHLBC, self.LDABCm, self.DECBC,
            self.INCr_c, self.DECr_c, self.LDrn_c, self.RRCA,
            # 10
            self.DJNZn, self.LDDEnn, self.LDDEmA, self.INCDE,
            self.INCr_d, self.DECr_d, self.LDrn_d, self.RLA,
            self.JRn, self.ADDHLDE, self.LDADEm, self.DECDE,
            self.INCr_e, self.DECr_e, self.LDrn_e, self.RRA,
            # 20
            self.JRNZn, self.LDHLnn, self.LDHLIA, self.INCHL,
            self.INCr_h, self.DECr_h, self.LDrn_h, self.DAA,
            self.JRZn, self.ADDHLHL, self.LDAHLI, self.DECHL,
            self.INCr_l, self.DECr_l, self.LDrn_l, self.CPL,
            # 30
            self.JRNCn, self.LDSPnn, self.LDHLDA, self.INCSP,
            self.INCHLm, self.DECHLm, self.LDHLmn, self.SCF,
            self.JRCn, self.ADDHLSP, self.LDAHLD, self.DECSP,
            self.INCr_a, self.DECr_a, self.LDrn_a, self.CCF,
            # 40
            self.LDrr_bb, self.LDrr_bc, self.LDrr_bd, self.LDrr_be,
            self.LDrr_bh, self.LDrr_bl, self.LDrHLm_b, self.LDrr_ba,
            self.LDrr_cb, self.LDrr_cc, self.LDrr_cd, self.LDrr_ce,
            self.LDrr_ch, self.LDrr_cl, self.LDrHLm_c, self.LDrr_ca,
            # 50
            self.LDrr_db, self.LDrr_dc, self.LDrr_dd, self.LDrr_de,
            self.LDrr_dh, self.LDrr_dl, self.LDrHLm_d, self.LDrr_da,
            self.LDrr_eb, self.LDrr_ec, self.LDrr_ed, self.LDrr_ee,
            self.LDrr_eh, self.LDrr_el, self.LDrHLm_e, self.LDrr_ea,
            # 60
            self.LDrr_hb, self.LDrr_hc, self.LDrr_hd, self.LDrr_he,
            self.LDrr_hh, self.LDrr_hl, self.LDrHLm_h, self.LDrr_ha,
            self.LDrr_lb, self.LDrr_lc, self.LDrr_ld, self.LDrr_le,
            self.LDrr_lh, self.LDrr_ll, self.LDrHLm_l, self.LDrr_la,
            # 70
            self.LDHLmr_b, self.LDHLmr_c, self.LDHLmr_d, self.LDHLmr_e,
            self.LDHLmr_h, self.LDHLmr_l, self.HALT, self.LDHLmr_a,
            self.LDrr_ab, self.LDrr_ac, self.LDrr_ad, self.LDrr_ae,
            self.LDrr_ah, self.LDrr_al, self.LDrHLm_a, self.LDrr_aa,
            # 80
            self.ADDr_b, self.ADDr_c, self.ADDr_d, self.ADDr_e,
            self.ADDr_h, self.ADDr_l, self.ADDHL, self.ADDr_a,
            self.ADCr_b, self.ADCr_c, self.ADCr_d, self.ADCr_e,
            self.ADCr_h, self.ADCr_l, self.ADCHL, self.ADCr_a,
            # 90
            self.SUBr_b, self.SUBr_c, self.SUBr_d, self.SUBr_e,
            self.SUBr_h, self.SUBr_l, self.SUBHL, self.SUBr_a,
            self.SBCr_b, self.SBCr_c, self.SBCr_d, self.SBCr_e,
            self.SBCr_h, self.SBCr_l, self.SBCHL, self.SBCr_a,
            # A0
            self.ANDr_b, self.ANDr_c, self.ANDr_d, self.ANDr_e,
            self.ANDr_h, self.ANDr_l, self.ANDHL, self.ANDr_a,
            self.XORr_b, self.XORr_c, self.XORr_d, self.XORr_e,
            self.XORr_h, self.XORr_l, self.XORHL, self.XORr_a,
            # B0
            self.ORr_b, self.ORr_c, self.ORr_d, self.ORr_e,
            self.ORr_h, self.ORr_l, self.ORHL, self.ORr_a,
            self.CPr_b, self.CPr_c, self.CPr_d, self.CPr_e,
            self.CPr_h, self.CPr_l, self.CPHL, self.CPr_a,
            # C0
            self.RETNZ, self.POPBC, self.JPNZnn, self.JPnn,
            self.CALLNZnn, self.PUSHBC, self.ADDn, self.RST00,
            self.RETZ, self.RET, self.JPZnn, self.MAPcb,
            self.CALLZnn, self.CALLnn, self.ADCn, self.RST08,
            # D0
            self.RETNC, self.POPDE, self.JPNCnn, self.XXX(0xd3),
            self.CALLNCnn, self.PUSHDE, self.SUBn, self.RST10,
            self.RETC, self.RETI, self.JPCnn, self.XXX(0xdb),
            self.CALLCnn, self.XXX(0xdd), self.SBCn, self.RST18,
            # E0
            self.LDIOnA, self.POPHL, self.LDIOCA, self.XXX(0xe3),
            self.XXX(0xe4), self.PUSHHL, self.ANDn, self.RST20,
            self.ADDSPn, self.JPHL, self.LDmmA, self.XXX(0xeb),
            self.XXX(0xec), self.XXX(0xed), self.XORn, self.RST28,
            # F0
            self.LDAIOn, self.POPAF, self.LDAIOC, self.DI,
            self.XXX(0xf4), self.PUSHAF, self.ORn, self.RST30,
            self.LDHLSPn, self.XXX(0xf9), self.LDAmm, self.EI,
            self.XXX(0xfc), self.XXX(0xfd), self.CPn, self.RST38]  #)))
        self._cbmap = [
            # CB00
            self.RLCr_b, self.RLCr_c, self.RLCr_d, self.RLCr_e,
            self.RLCr_h, self.RLCr_l, self.RLCHL, self.RLCr_a,
            self.RRCr_b, self.RRCr_c, self.RRCr_d, self.RRCr_e,
            self.RRCr_h, self.RRCr_l, self.RRCHL, self.RRCr_a,
            # CB10
            self.RLr_b, self.RLr_c, self.RLr_d, self.RLr_e,
            self.RLr_h, self.RLr_l, self.RLHL, self.RLr_a,
            self.RRr_b, self.RRr_c, self.RRr_d, self.RRr_e,
            self.RRr_h, self.RRr_l, self.RRHL, self.RRr_a,
            # CB20
            self.SLAr_b, self.SLAr_c, self.SLAr_d, self.SLAr_e,
            self.SLAr_h, self.SLAr_l, self.XX, self.SLAr_a,
            self.SRAr_b, self.SRAr_c, self.SRAr_d, self.SRAr_e,
            self.SRAr_h, self.SRAr_l, self.XX, self.SRAr_a,
            # CB30
            self.SWAPr_b, self.SWAPr_c, self.SWAPr_d, self.SWAPr_e,
            self.SWAPr_h, self.SWAPr_l, self.XX, self.SWAPr_a,
            self.SRLr_b, self.SRLr_c, self.SRLr_d, self.SRLr_e,
            self.SRLr_h, self.SRLr_l, self.XX, self.SRLr_a,
            # CB40
            self.BIT0b, self.BIT0c, self.BIT0d, self.BIT0e,
            self.BIT0h, self.BIT0l, self.BIT0m, self.BIT0a,
            self.BIT1b, self.BIT1c, self.BIT1d, self.BIT1e,
            self.BIT1h, self.BIT1l, self.BIT1m, self.BIT1a,
            # CB50
            self.BIT2b, self.BIT2c, self.BIT2d, self.BIT2e,
            self.BIT2h, self.BIT2l, self.BIT2m, self.BIT2a,
            self.BIT3b, self.BIT3c, self.BIT3d, self.BIT3e,
            self.BIT3h, self.BIT3l, self.BIT3m, self.BIT3a,
            # CB60
            self.BIT4b, self.BIT4c, self.BIT4d, self.BIT4e,
            self.BIT4h, self.BIT4l, self.BIT4m, self.BIT4a,
            self.BIT5b, self.BIT5c, self.BIT5d, self.BIT5e,
            self.BIT5h, self.BIT5l, self.BIT5m, self.BIT5a,
            # CB70
            self.BIT6b, self.BIT6c, self.BIT6d, self.BIT6e,
            self.BIT6h, self.BIT6l, self.BIT6m, self.BIT6a,
            self.BIT7b, self.BIT7c, self.BIT7d, self.BIT7e,
            self.BIT7h, self.BIT7l, self.BIT7m, self.BIT7a,
            # CB80
            self.RES0b, self.RES0c, self.RES0d, self.RES0e,
            self.RES0h, self.RES0l, self.RES0m, self.RES0a,
            self.RES1b, self.RES1c, self.RES1d, self.RES1e,
            self.RES1h, self.RES1l, self.RES1m, self.RES1a,
            # CB90
            self.RES2b, self.RES2c, self.RES2d, self.RES2e,
            self.RES2h, self.RES2l, self.RES2m, self.RES2a,
            self.RES3b, self.RES3c, self.RES3d, self.RES3e,
            self.RES3h, self.RES3l, self.RES3m, self.RES3a,
            # CBA0
            self.RES4b, self.RES4c, self.RES4d, self.RES4e,
            self.RES4h, self.RES4l, self.RES4m, self.RES4a,
            self.RES5b, self.RES5c, self.RES5d, self.RES5e,
            self.RES5h, self.RES5l, self.RES5m, self.RES5a,
            # CBB0
            self.RES6b, self.RES6c, self.RES6d, self.RES6e,
            self.RES6h, self.RES6l, self.RES6m, self.RES6a,
            self.RES7b, self.RES7c, self.RES7d, self.RES7e,
            self.RES7h, self.RES7l, self.RES7m, self.RES7a,
            # CBC0
            self.SET0b, self.SET0c, self.SET0d, self.SET0e,
            self.SET0h, self.SET0l, self.SET0m, self.SET0a,
            self.SET1b, self.SET1c, self.SET1d, self.SET1e,
            self.SET1h, self.SET1l, self.SET1m, self.SET1a,
            # CBD0
            self.SET2b, self.SET2c, self.SET2d, self.SET2e,
            self.SET2h, self.SET2l, self.SET2m, self.SET2a,
            self.SET3b, self.SET3c, self.SET3d, self.SET3e,
            self.SET3h, self.SET3l, self.SET3m, self.SET3a,
            # CBE0
            self.SET4b, self.SET4c, self.SET4d, self.SET4e,
            self.SET4h, self.SET4l, self.SET4m, self.SET4a,
            self.SET5b, self.SET5c, self.SET5d, self.SET5e,
            self.SET5h, self.SET5l, self.SET5m, self.SET5a,
            # CBF0
            self.SET6b, self.SET6c, self.SET6d, self.SET6e,
            self.SET6h, self.SET6l, self.SET6m, self.SET6a,
            self.SET7b, self.SET7c, self.SET7d, self.SET7e,
            self.SET7h, self.SET7l, self.SET7m, self.SET7a]

    def reset(self):
        self._HALT = 0
        self._STOP = 0

        self.R.reset()
        self.RSV.reset()
        self.CLOCK.reset()

        self.log.debug('reset')


    def exec(self):
        self.R.r = (self.R.r + 1) & 127
        self._map[self.mainboard.MMU.readByte(self.R.pc)]()
        self.R.pc += 1
        self.R.pc &= 65535
        self.CLOCK.m += self.R.m

    ###
    # Processor instructions
    ###

    # Load/Store
    def LDrr_bb(self):
        self.R.b = self.R.b
        self.R.m = 1

    def LDrr_bc(self):
        self.R.b = self.R.c
        self.R.m = 1

    def LDrr_bd(self):
        self.R.b = self.R.d
        self.R.m = 1

    def LDrr_be(self):
        self.R.b = self.R.e
        self.R.m = 1

    def LDrr_bh(self):
        self.R.b = self.R.h
        self.R.m = 1

    def LDrr_bl(self):
        self.R.b = self.R.l
        self.R.m = 1

    def LDrr_ba(self):
        self.R.b = self.R.a
        self.R.m = 1

    def LDrr_cb(self):
        self.R.c = self.R.b
        self.R.m = 1

    def LDrr_cc(self):
        self.R.c = self.R.c
        self.R.m = 1

    def LDrr_cd(self):
        self.R.c = self.R.d
        self.R.m = 1

    def LDrr_ce(self):
        self.R.c = self.R.e
        self.R.m = 1

    def LDrr_ch(self):
        self.R.c = self.R.h
        self.R.m = 1

    def LDrr_cl(self):
        self.R.c = self.R.l
        self.R.m = 1

    def LDrr_ca(self):
        self.R.c = self.R.a
        self.R.m = 1

    def LDrr_db(self):
        self.R.d = self.R.b
        self.R.m = 1

    def LDrr_dc(self):
        self.R.d = self.R.c
        self.R.m = 1

    def LDrr_dd(self):
        self.R.d = self.R.d
        self.R.m = 1

    def LDrr_de(self):
        self.R.d = self.R.e
        self.R.m = 1

    def LDrr_dh(self):
        self.R.d = self.R.h
        self.R.m = 1

    def LDrr_dl(self):
        self.R.d = self.R.l
        self.R.m = 1

    def LDrr_da(self):
        self.R.d = self.R.a
        self.R.m = 1

    def LDrr_eb(self):
        self.R.e = self.R.b
        self.R.m = 1

    def LDrr_ec(self):
        self.R.e = self.R.c
        self.R.m = 1

    def LDrr_ed(self):
        self.R.e = self.R.d
        self.R.m = 1

    def LDrr_ee(self):
        self.R.e = self.R.e
        self.R.m = 1

    def LDrr_eh(self):
        self.R.e = self.R.h
        self.R.m = 1

    def LDrr_el(self):
        self.R.e = self.R.l
        self.R.m = 1

    def LDrr_ea(self):
        self.R.e = self.R.a
        self.R.m = 1

    def LDrr_hb(self):
        self.R.h = self.R.b
        self.R.m = 1

    def LDrr_hc(self):
        self.R.h = self.R.c
        self.R.m = 1

    def LDrr_hd(self):
        self.R.h = self.R.d
        self.R.m = 1

    def LDrr_he(self):
        self.R.h = self.R.e
        self.R.m = 1

    def LDrr_hh(self):
        self.R.h = self.R.h
        self.R.m = 1

    def LDrr_hl(self):
        self.R.h = self.R.l
        self.R.m = 1

    def LDrr_ha(self):
        self.R.h = self.R.a
        self.R.m = 1

    def LDrr_lb(self):
        self.R.l = self.R.b
        self.R.m = 1

    def LDrr_lc(self):
        self.R.l = self.R.c
        self.R.m = 1

    def LDrr_ld(self):
        self.R.l = self.R.d
        self.R.m = 1

    def LDrr_le(self):
        self.R.l = self.R.e
        self.R.m = 1

    def LDrr_lh(self):
        self.R.l = self.R.h
        self.R.m = 1

    def LDrr_ll(self):
        self.R.l = self.R.l
        self.R.m = 1

    def LDrr_la(self):
        self.R.l = self.R.a
        self.R.m = 1

    def LDrr_ab(self):
        self.R.a = self.R.b
        self.R.m = 1

    def LDrr_ac(self):
        self.R.a = self.R.c
        self.R.m = 1

    def LDrr_ad(self):
        self.R.a = self.R.d
        self.R.m = 1

    def LDrr_ae(self):
        self.R.a = self.R.e
        self.R.m = 1

    def LDrr_ah(self):
        self.R.a = self.R.h
        self.R.m = 1

    def LDrr_al(self):
        self.R.a = self.R.l
        self.R.m = 1

    def LDrr_aa(self):
        self.R.a = self.R.a
        self.R.m = 1

    # ---
    def LDrHLm_b(self):
        self.R.b = self.mainboard.MMU.readByte((self.R.h << 8) + self.R.l)
        self.R.m = 2

    def LDrHLm_c(self):
        self.R.c = self.mainboard.MMU.readByte((self.R.h << 8) + self.R.l)
        self.R.m = 2

    def LDrHLm_d(self):
        self.R.d = self.mainboard.MMU.readByte((self.R.h << 8) + self.R.l)
        self.R.m = 2

    def LDrHLm_e(self):
        self.R.e = self.mainboard.MMU.readByte((self.R.h << 8) + self.R.l)
        self.R.m = 2

    def LDrHLm_h(self):
        self.R.h = self.mainboard.MMU.readByte((self.R.h << 8) + self.R.l)
        self.R.m = 2

    def LDrHLm_l(self):
        self.R.l = self.mainboard.MMU.readByte((self.R.h << 8) + self.R.l)
        self.R.m = 2

    def LDrHLm_a(self):
        self.R.a = self.mainboard.MMU.readByte((self.R.h << 8) + self.R.l)
        self.R.m = 2


    def LDHLmr_b(self):
        self.mainboard.MMU.writeByte((self.R.h << 8) + self.R.l, self.R.b)
        self.R.m = 2

    def LDHLmr_c(self):
        self.mainboard.MMU.writeByte((self.R.h << 8) + self.R.l, self.R.c)
        self.R.m = 2

    def LDHLmr_d(self):
        self.mainboard.MMU.writeByte((self.R.h << 8) + self.R.l, self.R.d)
        self.R.m = 2

    def LDHLmr_e(self):
        self.mainboard.MMU.writeByte((self.R.h << 8) + self.R.l, self.R.e)
        self.R.m = 2

    def LDHLmr_h(self):
        self.mainboard.MMU.writeByte((self.R.h << 8) + self.R.l, self.R.h)
        self.R.m = 2

    def LDHLmr_l(self):
        self.mainboard.MMU.writeByte((self.R.h << 8) + self.R.l, self.R.l)
        self.R.m = 2

    def LDHLmr_a(self):
        self.mainboard.MMU.writeByte((self.R.h << 8) + self.R.l, self.R.a)
        self.R.m = 2


    def LDrn_b(self):
        self.R.b = self.mainboard.MMU.readByte(self.R.pc)
        self.R.pc += 1
        self.R.m = 2

    def LDrn_c(self):
        self.R.c = self.mainboard.MMU.readByte(self.R.pc)
        self.R.pc += 1
        self.R.m = 2

    def LDrn_d(self):
        self.R.d = self.mainboard.MMU.readByte(self.R.pc)
        self.R.pc += 1
        self.R.m = 2

    def LDrn_e(self):
        self.R.e = self.mainboard.MMU.readByte(self.R.pc)
        self.R.pc += 1
        self.R.m = 2

    def LDrn_h(self):
        self.R.h = self.mainboard.MMU.readByte(self.R.pc)
        self.R.pc += 1
        self.R.m = 2

    def LDrn_l(self):
        self.R.l = self.mainboard.MMU.readByte(self.R.pc)
        self.R.pc += 1
        self.R.m = 2

    def LDrn_a(self):
        self.R.a = self.mainboard.MMU.readByte(self.R.pc)
        self.R.pc += 1
        self.R.m = 2


    def LDHLmn(self):
        self.mainboard.MMU.writeByte((self.R.h << 8) + self.R.l, self.mainboard.MMU.readByte(self.R.pc))
        self.R.pc += 1
        self.R.m = 3


    def LDBCmA(self):
        self.mainboard.MMU.writeByte((self.R.b << 8) + self.R.c, self.R.a)
        self.R.m = 2

    def LDDEmA(self):
        self.mainboard.MMU.writeByte((self.R.d << 8) + self.R.e, self.R.a)
        self.R.m = 2


    def LDmmA(self):
        self.mainboard.MMU.writeByte(self.mainboard.MMU.readWord(self.R.pc), self.R.a)
        self.R.pc += 2
        self.R.m = 4


    def LDABCm(self):
        self.R.a = self.mainboard.MMU.readByte((self.R.b << 8) + self.R.c)
        self.R.m = 2

    def LDADEm(self):
        self.R.a = self.mainboard.MMU.readByte((self.R.d << 8) + self.R.e)
        self.R.m = 2


    def LDAmm(self):
        self.R.a = self.mainboard.MMU.readByte(self.mainboard.MMU.readWord(self.R.pc))
        self.R.pc += 2
        self.R.m = 4


    def LDBCnn(self):
        self.R.c = self.mainboard.MMU.readByte(self.R.pc)
        self.R.b = self.mainboard.MMU.readByte(self.R.pc + 1)
        self.R.pc += 2
        self.R.m = 3

    def LDDEnn(self):
        self.R.e = self.mainboard.MMU.readByte(self.R.pc)
        self.R.d = self.mainboard.MMU.readByte(self.R.pc + 1)
        self.R.pc += 2
        self.R.m = 3

    def LDHLnn(self):
        self.R.l = self.mainboard.MMU.readByte(self.R.pc)
        self.R.h = self.mainboard.MMU.readByte(self.R.pc + 1)
        self.R.pc += 2
        self.R.m = 3

    def LDSPnn(self):
        self.R.sp = self.mainboard.MMU.readWord(self.R.pc)
        self.R.pc += 2
        self.R.m = 3


    def LDHLmm(self):
        i = self.mainboard.MMU.readWord(self.R.pc)
        self.R.pc += 2
        self.R.l = self.mainboard.MMU.readByte(i)
        self.R.h = self.mainboard.MMU.readByte(i + 1)
        self.R.m = 5

    def LDmmHL(self):
        i = self.mainboard.MMU.readWord(self.R.pc)
        self.R.pc += 2
        self.mainboard.MMU.writeWord(i, (self.R.h << 8) + self.R.l)
        self.R.m = 5

    def LDmmSP(self):
        i = self.mainboard.MMU.readWord(self.R.pc)
        self.R.pc += 2
        self.mainboard.MMU.writeWord(i, self.R.sp)
        self.R.m = 5

    def LDHLIA(self):
        self.mainboard.MMU.writeByte((self.R.h << 8) + self.R.l, self.R.a)
        self.R.l = (self.R.l + 1) & 255
        if not self.R.l:
            self.R.h = (self.R.h + 1) & 255
        self.R.m = 2

    def LDAHLI(self):
        self.R.a = self.mainboard.MMU.readByte((self.R.h << 8) + self.R.l)
        self.R.l = (self.R.l + 1) & 255
        if not self.R.l:
            self.R.h = (self.R.h + 1) & 255
        self.R.m = 2


    def LDHLDA(self):
        self.mainboard.MMU.writeByte((self.R.h << 8) + self.R.l, self.R.a)
        self.R.l = (self.R.l - 1) & 255
        if self.R.l == 255:
            self.R.h = (self.R.h - 1) & 255
        self.R.m = 2

    def LDAHLD(self):
        self.R.a = self.mainboard.MMU.readByte((self.R.h << 8) + self.R.l)
        self.R.l = (self.R.l - 1) & 255
        if self.R.l == 255:
            self.R.h = (self.R.h - 1) & 255
        self.R.m = 2


    def LDAIOn(self):
        self.R.a = self.mainboard.MMU.readByte(0xFF00 + self.mainboard.MMU.readByte(self.R.pc))
        self.R.pc += 1
        self.R.m = 3

    def LDIOnA(self):
        self.mainboard.MMU.writeByte(0xFF00 + self.mainboard.MMU.readByte(self.R.pc), self.R.a)
        self.R.pc += 1
        self.R.m = 3

    def LDAIOC(self):
        self.R.a = self.mainboard.MMU.readByte(0xFF00 + self.R.c)
        self.R.m = 2

    def LDIOCA(self):
        self.mainboard.MMU.writeByte(0xFF00 + self.R.c, self.R.a)
        self.R.m = 2


    def LDHLSPn(self):
        i = self.mainboard.MMU.readByte(self.R.pc)
        if i > 127:
            i = -((~i + 1) & 255)
        self.R.pc += 1
        i += self.R.sp
        self.R.h = (i >> 8) & 255
        self.R.l = i & 255
        self.R.m = 3


    def SWAPr_b(self):
        tr = self.R.b
        self.R.b = ((tr & 0xF) << 4) | ((tr & 0xF0) >> 4)
        self.R.f = 0 if self.R.b else 0x80
        self.R.m = 1

    def SWAPr_c(self):
        tr = self.R.c
        self.R.c = ((tr & 0xF) << 4) | ((tr & 0xF0) >> 4)
        self.R.f = 0 if self.R.c else 0x80
        self.R.m = 1

    def SWAPr_d(self):
        tr = self.R.d
        self.R.d = ((tr & 0xF) << 4) | ((tr & 0xF0) >> 4)
        self.R.f = 0 if self.R.d else 0x80
        self.R.m = 1

    def SWAPr_e(self):
        tr = self.R.e
        self.R.e = ((tr & 0xF) << 4) | ((tr & 0xF0) >> 4)
        self.R.f = 0 if self.R.e else 0x80
        self.R.m = 1

    def SWAPr_h(self):
        tr = self.R.h
        self.R.h = ((tr & 0xF) << 4) | ((tr & 0xF0) >> 4)
        self.R.f = 0 if self.R.h else 0x80
        self.R.m = 1

    def SWAPr_l(self):
        tr = self.R.l
        self.R.l = ((tr & 0xF) << 4) | ((tr & 0xF0) >> 4)
        self.R.f = 0 if self.R.l else 0x80
        self.R.m = 1

    def SWAPr_a(self):
        tr = self.R.a
        self.R.a = ((tr & 0xF) << 4) | ((tr & 0xF0) >> 4)
        self.R.f = 0 if self.R.a else 0x80
        self.R.m = 1

    # Data processing
    def ADDr_b(self):
        a = self.R.a
        self.R.a += self.R.b
        self.R.f = 0x10 if self.R.a > 255 else 0
        self.R.a &= 255
        if not self.R.a:
            self.R.f |= 0x80
        if (self.R.a ^ self.R.b ^ a) & 0x10:
            self.R.f |= 0x20
        self.R.m = 1

    def ADDr_c(self):
        a = self.R.a
        self.R.a += self.R.c
        self.R.f = 0x10 if self.R.a > 255 else 0
        self.R.a &= 255
        if not self.R.a:
            self.R.f |= 0x80
        if (self.R.a ^ self.R.c ^ a) & 0x10:
            self.R.f |= 0x20
        self.R.m = 1

    def ADDr_d(self):
        a = self.R.a
        self.R.a += self.R.d
        self.R.f = 0x10 if self.R.a > 255 else 0
        self.R.a &= 255
        if not self.R.a:
            self.R.f |= 0x80
        if (self.R.a ^ self.R.d ^ a) & 0x10:
            self.R.f |= 0x20
        self.R.m = 1

    def ADDr_e(self):
        a = self.R.a
        self.R.a += self.R.e
        self.R.f = 0x10 if self.R.a > 255 else 0
        self.R.a &= 255
        if not self.R.a:
            self.R.f |= 0x80
        if (self.R.a ^ self.R.e ^ a) & 0x10:
            self.R.f |= 0x20
        self.R.m = 1

    def ADDr_h(self):
        a = self.R.a
        self.R.a += self.R.h
        self.R.f = 0x10 if self.R.a > 255 else 0
        self.R.a &= 255
        if not self.R.a:
            self.R.f |= 0x80
        if (self.R.a ^ self.R.h ^ a) & 0x10:
            self.R.f |= 0x20
        self.R.m = 1

    def ADDr_l(self):
        a = self.R.a
        self.R.a += self.R.l
        self.R.f = 0x10 if self.R.a > 255 else 0
        self.R.a &= 255
        if not self.R.a:
            self.R.f |= 0x80
        if (self.R.a ^ self.R.l ^ a) & 0x10:
            self.R.f |= 0x20
        self.R.m = 1

    def ADDr_a(self):
        a = self.R.a
        self.R.a += self.R.a
        self.R.f = 0x10 if self.R.a > 255 else 0
        self.R.a &= 255
        if not self.R.a:
            self.R.f |= 0x80
        if (self.R.a ^ self.R.a ^ a) & 0x10:
            self.R.f |= 0x20
        self.R.m = 1

    def ADDHL(self):
        a = self.R.a
        m = self.mainboard.MMU.readByte((self.R.h << 8) + self.R.l)
        self.R.a += m
        self.R.f = 0x10 if self.R.a > 255 else 0
        self.R.a &= 255
        if not self.R.a:
            self.R.f |= 0x80
        if (self.R.a ^ a ^ m) & 0x10:
            self.R.f |= 0x20
        self.R.m = 2

    def ADDn(self):
        a = self.R.a
        m = self.mainboard.MMU.readByte(self.R.pc)
        self.R.a += m
        self.R.pc += 1
        self.R.f = 0x10 if self.R.a > 255 else 0
        self.R.a &= 255
        if not self.R.a:
            self.R.f |= 0x80
        if (self.R.a ^ a ^ m) & 0x10:
            self.R.f |= 0x20
        self.R.m = 2

    def ADDHLBC(self):
        hl = (self.R.h << 8) + self.R.l
        hl += (self.R.b << 8) + self.R.c
        if hl > 65535:
            self.R.f |= 0x10
        else:
            self.R.f &= 0xEF
        self.R.h = (hl >> 8) & 255
        self.R.l = hl & 255
        self.R.m = 3

    def ADDHLDE(self):
        hl = (self.R.h << 8) + self.R.l
        hl += (self.R.d << 8) + self.R.e
        if hl > 65535:
            self.R.f |= 0x10
        else:
            self.R.f &= 0xEF
        self.R.h = (hl >> 8) & 255
        self.R.l = hl & 255
        self.R.m = 3

    def ADDHLHL(self):
        hl = (self.R.h << 8) + self.R.l
        hl += (self.R.h << 8) + self.R.l
        if hl > 65535:
            self.R.f |= 0x10
        else:
            self.R.f &= 0xEF
        self.R.h = (hl >> 8) & 255
        self.R.l = hl & 255
        self.R.m = 3

    def ADDHLSP(self):
        hl = (self.R.h << 8) + self.R.l
        hl += self.R.sp
        if hl > 65535:
            self.R.f |= 0x10
        else:
            self.R.f &= 0xEF
        self.R.h = (hl >> 8) & 255
        self.R.l = hl & 255
        self.R.m = 3

    def ADDSPn(self):
        i = self.mainboard.MMU.readByte(self.R.pc)
        if i > 127:
            i = -((~i + 1) & 255)
        self.R.pc += 1
        self.R.sp += i
        self.R.m = 4


    def ADCr_b(self):
        a = self.R.a
        self.R.a += self.R.b
        self.R.a += 1 if self.R.f & 0x10 else 0
        self.R.f = 0x10 if self.R.a > 255 else 0
        self.R.a &= 255
        if not self.R.a:
            self.R.f |= 0x80
        if (self.R.a ^ self.R.b ^ a) & 0x10:
            self.R.f |= 0x20
        self.R.m = 1

    def ADCr_c(self):
        a = self.R.a
        self.R.a += self.R.c
        self.R.a += 1 if self.R.f & 0x10 else 0
        self.R.f = 0x10 if self.R.a > 255 else 0
        self.R.a &= 255
        if not self.R.a:
            self.R.f |= 0x80
        if (self.R.a ^ self.R.c ^ a) & 0x10:
            self.R.f |= 0x20
        self.R.m = 1

    def ADCr_d(self):
        a = self.R.a
        self.R.a += self.R.d
        self.R.a += 1 if self.R.f & 0x10 else 0
        self.R.f = 0x10 if self.R.a > 255 else 0
        self.R.a &= 255
        if not self.R.a:
            self.R.f |= 0x80
        if (self.R.a ^ self.R.d ^ a) & 0x10:
            self.R.f |= 0x20
        self.R.m = 1

    def ADCr_e(self):
        a = self.R.a
        self.R.a += self.R.e
        self.R.a += 1 if self.R.f & 0x10 else 0
        self.R.f = 0x10 if self.R.a > 255 else 0
        self.R.a &= 255
        if not self.R.a:
            self.R.f |= 0x80
        if (self.R.a ^ self.R.e ^ a) & 0x10:
            self.R.f |= 0x20
        self.R.m = 1

    def ADCr_h(self):
        a = self.R.a
        self.R.a += self.R.h
        self.R.a += 1 if self.R.f & 0x10 else 0
        self.R.f = 0x10 if self.R.a > 255 else 0
        self.R.a &= 255
        if not self.R.a:
            self.R.f |= 0x80
        if (self.R.a ^ self.R.h ^ a) & 0x10:
            self.R.f |= 0x20
        self.R.m = 1

    def ADCr_l(self):
        a = self.R.a
        self.R.a += self.R.l
        self.R.a += 1 if self.R.f & 0x10 else 0
        self.R.f = 0x10 if self.R.a > 255 else 0
        self.R.a &= 255
        if not self.R.a:
            self.R.f |= 0x80
        if (self.R.a ^ self.R.l ^ a) & 0x10:
            self.R.f |= 0x20
        self.R.m = 1

    def ADCr_a(self):
        a = self.R.a
        self.R.a += self.R.a
        self.R.a += 1 if self.R.f & 0x10 else 0
        self.R.f = 0x10 if self.R.a > 255 else 0
        self.R.a &= 255
        if not self.R.a:
            self.R.f |= 0x80
        if (self.R.a ^ self.R.a ^ a) & 0x10:
            self.R.f |= 0x20
        self.R.m = 1

    def ADCHL(self):
        a = self.R.a
        m = self.mainboard.MMU.readByte((self.R.h << 8) + self.R.l)
        self.R.a += m
        self.R.a += 1 if self.R.f & 0x10 else 0
        self.R.f = 0x10 if self.R.a > 255 else 0
        self.R.a &= 255
        if not self.R.a:
            self.R.f |= 0x80
        if (self.R.a ^ m ^ a) & 0x10:
            self.R.f |= 0x20
        self.R.m = 2

    def ADCn(self):
        a = self.R.a
        m = self.mainboard.MMU.readByte(self.R.pc)
        self.R.a += m
        self.R.pc += 1
        self.R.a += 1 if self.R.f & 0x10 else 0
        self.R.f = 0x10 if self.R.a > 255 else 0
        self.R.a &= 255
        if not self.R.a:
            self.R.f |= 0x80
        if (self.R.a ^ m ^ a) & 0x10:
            self.R.f |= 0x20
        self.R.m = 2


    def SUBr_b(self):
        a = self.R.a
        self.R.a -= self.R.b
        self.R.f = 0x50 if self.R.a < 0 else 0x40
        self.R.a &= 255
        if not self.R.a:
            self.R.f |= 0x80
        if (self.R.a ^ self.R.b ^ a) & 0x10:
            self.R.f |= 0x20
        self.R.m = 1

    def SUBr_c(self):
        a = self.R.a
        self.R.a -= self.R.c
        self.R.f = 0x50 if self.R.a < 0 else 0x40
        self.R.a &= 255
        if not self.R.a:
            self.R.f |= 0x80
        if (self.R.a ^ self.R.c ^ a) & 0x10:
            self.R.f |= 0x20
        self.R.m = 1

    def SUBr_d(self):
        a = self.R.a
        self.R.a -= self.R.d
        self.R.f = 0x50 if self.R.a < 0 else 0x40
        self.R.a &= 255
        if not self.R.a:
            self.R.f |= 0x80
        if (self.R.a ^ self.R.d ^ a) & 0x10:
            self.R.f |= 0x20
        self.R.m = 1

    def SUBr_e(self):
        a = self.R.a
        self.R.a -= self.R.e
        self.R.f = 0x50 if self.R.a < 0 else 0x40
        self.R.a &= 255
        if not self.R.a:
            self.R.f |= 0x80
        if (self.R.a ^ self.R.e ^ a) & 0x10:
            self.R.f |= 0x20
        self.R.m = 1

    def SUBr_h(self):
        a = self.R.a
        self.R.a -= self.R.h
        self.R.f = 0x50 if self.R.a < 0 else 0x40
        self.R.a &= 255
        if not self.R.a:
            self.R.f |= 0x80
        if (self.R.a ^ self.R.h ^ a) & 0x10:
            self.R.f |= 0x20
        self.R.m = 1

    def SUBr_l(self):
        a = self.R.a
        self.R.a -= self.R.l
        self.R.f = 0x50 if self.R.a < 0 else 0x40
        self.R.a &= 255
        if not self.R.a:
            self.R.f |= 0x80
        if (self.R.a ^ self.R.l ^ a) & 0x10:
            self.R.f |= 0x20
        self.R.m = 1

    def SUBr_a(self):
        a = self.R.a
        self.R.a -= self.R.a
        self.R.f = 0x50 if self.R.a < 0 else 0x40
        self.R.a &= 255
        if not self.R.a:
            self.R.f |= 0x80
        if (self.R.a ^ self.R.a ^ a) & 0x10:
            self.R.f |= 0x20
        self.R.m = 1

    def SUBHL(self):
        a = self.R.a
        m = self.mainboard.MMU.readByte((self.R.h << 8) + self.R.l)
        self.R.a -= m
        self.R.f = 0x50 if self.R.a < 0 else 0x40
        self.R.a &= 255
        if not self.R.a:
            self.R.f |= 0x80
        if (self.R.a ^ m ^ a) & 0x10:
            self.R.f |= 0x20
        self.R.m = 2

    def SUBn(self):
        a = self.R.a
        m = self.mainboard.MMU.readByte(self.R.pc)
        self.R.a -= m
        self.R.pc += 1
        self.R.f = 0x50 if self.R.a < 0 else 0x40
        self.R.a &= 255
        if not self.R.a:
            self.R.f |= 0x80
        if (self.R.a ^ m ^ a) & 0x10:
            self.R.f |= 0x20
        self.R.m = 2


    def SBCr_b(self):
        a = self.R.a
        self.R.a -= self.R.b
        self.R.a -= 1 if self.R.f & 0x10 else 0
        self.R.f = 0x50 if self.R.a < 0 else 0x40
        self.R.a &= 255
        if not self.R.a:
            self.R.f |= 0x80
        if (self.R.a ^ self.R.b ^ a) & 0x10:
            self.R.f |= 0x20
        self.R.m = 1

    def SBCr_c(self):
        a = self.R.a
        self.R.a -= self.R.c
        self.R.a -= 1 if self.R.f & 0x10 else 0
        self.R.f = 0x50 if self.R.a < 0 else 0x40
        self.R.a &= 255
        if not self.R.a:
            self.R.f |= 0x80
        if (self.R.a ^ self.R.c ^ a) & 0x10:
            self.R.f |= 0x20
        self.R.m = 1

    def SBCr_d(self):
        a = self.R.a
        self.R.a -= self.R.d
        self.R.a -= 1 if self.R.f & 0x10 else 0
        self.R.f = 0x50 if self.R.a < 0 else 0x40
        self.R.a &= 255
        if not self.R.a:
            self.R.f |= 0x80
        if (self.R.a ^ self.R.d ^ a) & 0x10:
            self.R.f |= 0x20
        self.R.m = 1

    def SBCr_e(self):
        a = self.R.a
        self.R.a -= self.R.e
        self.R.a -= 1 if self.R.f & 0x10 else 0
        self.R.f = 0x50 if self.R.a < 0 else 0x40
        self.R.a &= 255
        if not self.R.a:
            self.R.f |= 0x80
        if (self.R.a ^ self.R.e ^ a) & 0x10:
            self.R.f |= 0x20
        self.R.m = 1

    def SBCr_h(self):
        a = self.R.a
        self.R.a -= self.R.h
        self.R.a -= 1 if self.R.f & 0x10 else 0
        self.R.f = 0x50 if self.R.a < 0 else 0x40
        self.R.a &= 255
        if not self.R.a:
            self.R.f |= 0x80
        if (self.R.a ^ self.R.h ^ a) & 0x10:
            self.R.f |= 0x20
        self.R.m = 1

    def SBCr_l(self):
        a = self.R.a
        self.R.a -= self.R.l
        self.R.a -= 1 if self.R.f & 0x10 else 0
        self.R.f = 0x50 if self.R.a < 0 else 0x40
        self.R.a &= 255
        if not self.R.a:
            self.R.f |= 0x80
        if (self.R.a ^ self.R.l ^ a) & 0x10:
            self.R.f |= 0x20
        self.R.m = 1

    def SBCr_a(self):
        a = self.R.a
        self.R.a -= self.R.a
        self.R.a -= 1 if self.R.f & 0x10 else 0
        self.R.f = 0x50 if self.R.a < 0 else 0x40
        self.R.a &= 255
        if not self.R.a:
            self.R.f |= 0x80
        if (self.R.a ^ self.R.a ^ a) & 0x10:
            self.R.f |= 0x20
        self.R.m = 1

    def SBCHL(self):
        a = self.R.a
        m = self.mainboard.MMU.readByte((self.R.h << 8) + self.R.l)
        self.R.a -= m
        self.R.a -= 1 if self.R.f & 0x10 else 0
        self.R.f = 0x50 if self.R.a < 0 else 0x40
        self.R.a &= 255
        if not self.R.a:
            self.R.f |= 0x80
        if (self.R.a ^ m ^ a) & 0x10:
            self.R.f |= 0x20
        self.R.m = 2

    def SBCn(self):
        a = self.R.a
        m = self.mainboard.MMU.readByte(self.R.pc)
        self.R.a -= m
        self.R.pc += 1
        self.R.a -= 1 if self.R.f & 0x10 else 0
        self.R.f = 0x50 if self.R.a < 0 else 0x40
        self.R.a &= 255
        if not self.R.a:
            self.R.f |= 0x80
        if (self.R.a ^ m ^ a) & 0x10:
            self.R.f |= 0x20
        self.R.m = 2


    def CPr_b(self):
        i = self.R.a
        i -= self.R.b
        self.R.f = 0x50 if i < 0 else 0x40
        i &= 255
        if not i:
            self.R.f |= 0x80
        if (self.R.a ^ self.R.b ^ i) & 0x10:
            self.R.f |= 0x20
        self.R.m = 1

    def CPr_c(self):
        i = self.R.a
        i -= self.R.c
        self.R.f = 0x50 if i < 0 else 0x40
        i &= 255
        if not i:
            self.R.f |= 0x80
        if (self.R.a ^ self.R.c ^ i) & 0x10:
            self.R.f |= 0x20
        self.R.m = 1

    def CPr_d(self):
        i = self.R.a
        i -= self.R.d
        self.R.f = 0x50 if i < 0 else 0x40
        i &= 255
        if not i:
            self.R.f |= 0x80
        if (self.R.a ^ self.R.d ^ i) & 0x10:
            self.R.f |= 0x20
        self.R.m = 1

    def CPr_e(self):
        i = self.R.a
        i -= self.R.e
        self.R.f = 0x50 if i < 0 else 0x40
        i &= 255
        if not i:
            self.R.f |= 0x80
        if (self.R.a ^ self.R.e ^ i) & 0x10:
            self.R.f |= 0x20
        self.R.m = 1

    def CPr_h(self):
        i = self.R.a
        i -= self.R.h
        self.R.f = 0x50 if i < 0 else 0x40
        i &= 255
        if not i:
            self.R.f |= 0x80
        if (self.R.a ^ self.R.h ^ i) & 0x10:
            self.R.f |= 0x20
        self.R.m = 1

    def CPr_l(self):
        i = self.R.a
        i -= self.R.l
        self.R.f = 0x50 if i < 0 else 0x40
        i &= 255
        if not i:
            self.R.f |= 0x80
        if (self.R.a ^ self.R.l ^ i) & 0x10:
            self.R.f |= 0x20
        self.R.m = 1

    def CPr_a(self):
        i = self.R.a
        i -= self.R.a
        self.R.f = 0x50 if i < 0 else 0x40
        i &= 255
        if not i:
            self.R.f |= 0x80
        if (self.R.a ^ self.R.a ^ i) & 0x10:
            self.R.f |= 0x20
        self.R.m = 1

    def CPHL(self):
        i = self.R.a
        m = self.mainboard.MMU.readByte((self.R.h << 8) + self.R.l)
        i -= m
        self.R.f = 0x50 if i < 0 else 0x40
        i &= 255
        if not i:
            self.R.f |= 0x80
        if (self.R.a ^ i ^ m) & 0x10:
            self.R.f |= 0x20
        self.R.m = 2

    def CPn(self):
        i = self.R.a
        m = self.mainboard.MMU.readByte(self.R.pc)
        i -= m
        self.R.pc += 1
        self.R.f = 0x50 if i < 0 else 0x40
        i &= 255
        if not i:
            self.R.f |= 0x80
        if (self.R.a ^ i ^ m) & 0x10:
            self.R.f |= 0x20
        self.R.m = 2


    def DAA(self):
        a = self.R.a

        if (self.R.f & 0x20) or ((self.R.a & 15) > 9):
            self.R.a += 6

        self.R.f &= 0xEF

        if (self.R.f & 0x20) or (a > 0x99):
            self.R.a += 0x60
            self.R.f |= 0x10

        self.R.m = 1


    def ANDr_b(self):
        self.R.a &= self.R.b
        self.R.a &= 255
        self.R.f = 0 if self.R.a else 0x80
        self.R.m = 1

    def ANDr_c(self):
        self.R.a &= self.R.c
        self.R.a &= 255
        self.R.f = 0 if self.R.a else 0x80
        self.R.m = 1

    def ANDr_d(self):
        self.R.a &= self.R.d
        self.R.a &= 255
        self.R.f = 0 if self.R.a else 0x80
        self.R.m = 1

    def ANDr_e(self):
        self.R.a &= self.R.e
        self.R.a &= 255
        self.R.f = 0 if self.R.a else 0x80
        self.R.m = 1

    def ANDr_h(self):
        self.R.a &= self.R.h
        self.R.a &= 255
        self.R.f = 0 if self.R.a else 0x80
        self.R.m = 1

    def ANDr_l(self):
        self.R.a &= self.R.l
        self.R.a &= 255
        self.R.f = 0 if self.R.a else 0x80
        self.R.m = 1

    def ANDr_a(self):
        self.R.a &= self.R.a
        self.R.a &= 255
        self.R.f = 0 if self.R.a else 0x80
        self.R.m = 1

    def ANDHL(self):
        self.R.a &= self.mainboard.MMU.readByte((self.R.h << 8) + self.R.l)
        self.R.a &= 255
        self.R.f = 0 if self.R.a else 0x80
        self.R.m = 2

    def ANDn(self):
        self.R.a &= self.mainboard.MMU.readByte(self.R.pc)
        self.R.pc += 1
        self.R.a &= 255
        self.R.f = 0 if self.R.a else 0x80
        self.R.m = 2


    def ORr_b(self):
        self.R.a |= self.R.b
        self.R.a &= 255
        self.R.f = 0 if self.R.a else 0x80
        self.R.m = 1

    def ORr_c(self):
        self.R.a |= self.R.c
        self.R.a &= 255
        self.R.f = 0 if self.R.a else 0x80
        self.R.m = 1

    def ORr_d(self):
        self.R.a |= self.R.d
        self.R.a &= 255
        self.R.f = 0 if self.R.a else 0x80
        self.R.m = 1

    def ORr_e(self):
        self.R.a |= self.R.e
        self.R.a &= 255
        self.R.f = 0 if self.R.a else 0x80
        self.R.m = 1

    def ORr_h(self):
        self.R.a |= self.R.h
        self.R.a &= 255
        self.R.f = 0 if self.R.a else 0x80
        self.R.m = 1

    def ORr_l(self):
        self.R.a |= self.R.l
        self.R.a &= 255
        self.R.f = 0 if self.R.a else 0x80
        self.R.m = 1

    def ORr_a(self):
        self.R.a |= self.R.a
        self.R.a &= 255
        self.R.f = 0 if self.R.a else 0x80
        self.R.m = 1

    def ORHL(self):
        self.R.a |= self.mainboard.MMU.readByte((self.R.h << 8) + self.R.l)
        self.R.a &= 255
        self.R.f = 0 if self.R.a else 0x80
        self.R.m = 2

    def ORn(self):
        self.R.a |= self.mainboard.MMU.readByte(self.R.pc)
        self.R.pc += 1
        self.R.a &= 255
        self.R.f = 0 if self.R.a else 0x80
        self.R.m = 2


    def XORr_b(self):
        self.R.a ^= self.R.b
        self.R.a &= 255
        self.R.f = 0 if self.R.a else 0x80
        self.R.m = 1

    def XORr_c(self):
        self.R.a ^= self.R.c
        self.R.a &= 255
        self.R.f = 0 if self.R.a else 0x80
        self.R.m = 1

    def XORr_d(self):
        self.R.a ^= self.R.d
        self.R.a &= 255
        self.R.f = 0 if self.R.a else 0x80
        self.R.m = 1

    def XORr_e(self):
        self.R.a ^= self.R.e
        self.R.a &= 255
        self.R.f = 0 if self.R.a else 0x80
        self.R.m = 1

    def XORr_h(self):
        self.R.a ^= self.R.h
        self.R.a &= 255
        self.R.f = 0 if self.R.a else 0x80
        self.R.m = 1

    def XORr_l(self):
        self.R.a ^= self.R.l
        self.R.a &= 255
        self.R.f = 0 if self.R.a else 0x80
        self.R.m = 1

    def XORr_a(self):
        self.R.a ^= self.R.a
        self.R.a &= 255
        self.R.f = 0 if self.R.a else 0x80
        self.R.m = 1

    def XORHL(self):
        self.R.a ^= self.mainboard.MMU.readByte((self.R.h << 8) + self.R.l)
        self.R.a &= 255
        self.R.f = 0 if self.R.a else 0x80
        self.R.m = 2

    def XORn(self):
        self.R.a ^= self.mainboard.MMU.readByte(self.R.pc)
        self.R.pc += 1
        self.R.a &= 255
        self.R.f = 0 if self.R.a else 0x80
        self.R.m = 2


    def INCr_b(self):
        self.R.b += 1
        self.R.b &= 255
        self.R.f = 0 if self.R.b else 0x80
        self.R.m = 1

    def INCr_c(self):
        self.R.c += 1
        self.R.c &= 255
        self.R.f = 0 if self.R.c else 0x80
        self.R.m = 1

    def INCr_d(self):
        self.R.d += 1
        self.R.d &= 255
        self.R.f = 0 if self.R.d else 0x80
        self.R.m = 1

    def INCr_e(self):
        self.R.e += 1
        self.R.e &= 255
        self.R.f = 0 if self.R.e else 0x80
        self.R.m = 1

    def INCr_h(self):
        self.R.h += 1
        self.R.h &= 255
        self.R.f = 0 if self.R.h else 0x80
        self.R.m = 1

    def INCr_l(self):
        self.R.l += 1
        self.R.l &= 255
        self.R.f = 0 if self.R.l else 0x80
        self.R.m = 1

    def INCr_a(self):
        self.R.a += 1
        self.R.a &= 255
        self.R.f = 0 if self.R.a else 0x80
        self.R.m = 1

    def INCHLm(self):
        i = self.mainboard.MMU.readByte((self.R.h << 8) + self.R.l) + 1
        i &= 255
        self.mainboard.MMU.writeByte((self.R.h << 8) + self.R.l, i)
        self.R.f = 0 if i else 0x80
        self.R.m = 3


    def DECr_b(self):
        self.R.b -= 1
        self.R.b &= 255
        self.R.f = 0 if self.R.b else 0x80
        self.R.m = 1

    def DECr_c(self):
        self.R.c -= 1
        self.R.c &= 255
        self.R.f = 0 if self.R.c else 0x80
        self.R.m = 1

    def DECr_d(self):
        self.R.d -= 1
        self.R.d &= 255
        self.R.f = 0 if self.R.d else 0x80
        self.R.m = 1

    def DECr_e(self):
        self.R.e -= 1
        self.R.e &= 255
        self.R.f = 0 if self.R.e else 0x80
        self.R.m = 1

    def DECr_h(self):
        self.R.h -= 1
        self.R.h &= 255
        self.R.f = 0 if self.R.h else 0x80
        self.R.m = 1

    def DECr_l(self):
        self.R.l -= 1
        self.R.l &= 255
        self.R.f = 0 if self.R.l else 0x80
        self.R.m = 1

    def DECr_a(self):
        self.R.a -= 1
        self.R.a &= 255
        self.R.f = 0 if self.R.a else 0x80
        self.R.m = 1

    def DECHLm(self):
        i = self.mainboard.MMU.readByte((self.R.h << 8) + self.R.l) - 1
        i &= 255
        self.mainboard.MMU.writeByte((self.R.h << 8) + self.R.l, i)
        self.R.f = 0 if i else 0x80
        self.R.m = 3


    def INCBC(self):
        self.R.c = (self.R.c + 1) & 255
        if not self.R.c:
            self.R.b = (self.R.b + 1) & 255
        self.R.m = 1

    def INCDE(self):
        self.R.e = (self.R.e + 1) & 255
        if not self.R.e:
            self.R.d = (self.R.d + 1) & 255
        self.R.m = 1

    def INCHL(self):
        self.R.l = (self.R.l + 1) & 255
        if not self.R.l:
            self.R.h = (self.R.h + 1) & 255
        self.R.m = 1

    def INCSP(self):
        self.R.sp = (self.R.sp + 1) & 65535
        self.R.m = 1


    def DECBC(self):
        self.R.c = (self.R.c - 1) & 255
        if self.R.c == 255:
            self.R.b = (self.R.b - 1) & 255
        self.R.m = 1

    def DECDE(self):
        self.R.e = (self.R.e - 1) & 255
        if self.R.e == 255:
            self.R.d = (self.R.d - 1) & 255
        self.R.m = 1

    def DECHL(self):
        self.R.l = (self.R.l - 1) & 255
        if self.R.l == 255:
            self.R.h = (self.R.h - 1) & 255
        self.R.m = 1

    def DECSP(self):
        self.R.sp = (self.R.sp - 1) & 65535
        self.R.m = 1


        # --- Bit manipulation ---

    def BIT0b(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.b & 0x01 else 0x80
        self.R.m = 2

    def BIT0c(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.c & 0x01 else 0x80
        self.R.m = 2

    def BIT0d(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.d & 0x01 else 0x80
        self.R.m = 2

    def BIT0e(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.e & 0x01 else 0x80
        self.R.m = 2

    def BIT0h(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.h & 0x01 else 0x80
        self.R.m = 2

    def BIT0l(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.l & 0x01 else 0x80
        self.R.m = 2

    def BIT0a(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.a & 0x01 else 0x80
        self.R.m = 2

    def BIT0m(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.mainboard.MMU.readByte((self.R.h << 8) + self.R.l) & 0x01 else 0x80
        self.R.m = 3


    def RES0b(self):
        self.R.b &= 0xFE
        self.R.m = 2

    def RES0c(self):
        self.R.c &= 0xFE
        self.R.m = 2

    def RES0d(self):
        self.R.d &= 0xFE
        self.R.m = 2

    def RES0e(self):
        self.R.e &= 0xFE
        self.R.m = 2

    def RES0h(self):
        self.R.h &= 0xFE
        self.R.m = 2

    def RES0l(self):
        self.R.l &= 0xFE
        self.R.m = 2

    def RES0a(self):
        self.R.a &= 0xFE
        self.R.m = 2

    def RES0m(self):
        i = self.mainboard.MMU.readByte((self.R.h << 8) + self.R.l)
        i &= 0xFE
        self.mainboard.MMU.writeByte((self.R.h << 8) + self.R.l, i)
        self.R.m = 4


    def SET0b(self):
        self.R.b |= 0x01
        self.R.m = 2

    def SET0c(self):
        self.R.b |= 0x01
        self.R.m = 2

    def SET0d(self):
        self.R.b |= 0x01
        self.R.m = 2

    def SET0e(self):
        self.R.b |= 0x01
        self.R.m = 2

    def SET0h(self):
        self.R.b |= 0x01
        self.R.m = 2

    def SET0l(self):
        self.R.b |= 0x01
        self.R.m = 2

    def SET0a(self):
        self.R.b |= 0x01
        self.R.m = 2

    def SET0m(self):
        i = self.mainboard.MMU.readByte((self.R.h << 8) + self.R.l)
        i |= 0x01
        self.mainboard.MMU.writeByte((self.R.h << 8) + self.R.l, i)
        self.R.m = 4


    def BIT1b(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.b & 0x02 else 0x80
        self.R.m = 2

    def BIT1c(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.c & 0x02 else 0x80
        self.R.m = 2

    def BIT1d(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.d & 0x02 else 0x80
        self.R.m = 2

    def BIT1e(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.e & 0x02 else 0x80
        self.R.m = 2

    def BIT1h(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.h & 0x02 else 0x80
        self.R.m = 2

    def BIT1l(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.l & 0x02 else 0x80
        self.R.m = 2

    def BIT1a(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.a & 0x02 else 0x80
        self.R.m = 2

    def BIT1m(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.mainboard.MMU.readByte((self.R.h << 8) + self.R.l) & 0x02 else 0x80
        self.R.m = 3


    def RES1b(self):
        self.R.b &= 0xFD
        self.R.m = 2

    def RES1c(self):
        self.R.c &= 0xFD
        self.R.m = 2

    def RES1d(self):
        self.R.d &= 0xFD
        self.R.m = 2

    def RES1e(self):
        self.R.e &= 0xFD
        self.R.m = 2

    def RES1h(self):
        self.R.h &= 0xFD
        self.R.m = 2

    def RES1l(self):
        self.R.l &= 0xFD
        self.R.m = 2

    def RES1a(self):
        self.R.a &= 0xFD
        self.R.m = 2

    def RES1m(self):
        i = self.mainboard.MMU.readByte((self.R.h << 8) + self.R.l)
        i &= 0xFD
        self.mainboard.MMU.writeByte((self.R.h << 8) + self.R.l, i)
        self.R.m = 4


    def SET1b(self):
        self.R.b |= 0x02
        self.R.m = 2

    def SET1c(self):
        self.R.b |= 0x02
        self.R.m = 2

    def SET1d(self):
        self.R.b |= 0x02
        self.R.m = 2

    def SET1e(self):
        self.R.b |= 0x02
        self.R.m = 2

    def SET1h(self):
        self.R.b |= 0x02
        self.R.m = 2

    def SET1l(self):
        self.R.b |= 0x02
        self.R.m = 2

    def SET1a(self):
        self.R.b |= 0x02
        self.R.m = 2

    def SET1m(self):
        i = self.mainboard.MMU.readByte((self.R.h << 8) + self.R.l)
        i |= 0x02
        self.mainboard.MMU.writeByte((self.R.h << 8) + self.R.l, i)
        self.R.m = 4


    def BIT2b(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.b & 0x04 else 0x80
        self.R.m = 2

    def BIT2c(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.c & 0x04 else 0x80
        self.R.m = 2

    def BIT2d(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.d & 0x04 else 0x80
        self.R.m = 2

    def BIT2e(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.e & 0x04 else 0x80
        self.R.m = 2

    def BIT2h(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.h & 0x04 else 0x80
        self.R.m = 2

    def BIT2l(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.l & 0x04 else 0x80
        self.R.m = 2

    def BIT2a(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.a & 0x04 else 0x80
        self.R.m = 2

    def BIT2m(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.mainboard.MMU.readByte((self.R.h << 8) + self.R.l) & 0x04 else 0x80
        self.R.m = 3


    def RES2b(self):
        self.R.b &= 0xFB
        self.R.m = 2

    def RES2c(self):
        self.R.c &= 0xFB
        self.R.m = 2

    def RES2d(self):
        self.R.d &= 0xFB
        self.R.m = 2

    def RES2e(self):
        self.R.e &= 0xFB
        self.R.m = 2

    def RES2h(self):
        self.R.h &= 0xFB
        self.R.m = 2

    def RES2l(self):
        self.R.l &= 0xFB
        self.R.m = 2

    def RES2a(self):
        self.R.a &= 0xFB
        self.R.m = 2

    def RES2m(self):
        i = self.mainboard.MMU.readByte((self.R.h << 8) + self.R.l)
        i &= 0xFB
        self.mainboard.MMU.writeByte((self.R.h << 8) + self.R.l, i)
        self.R.m = 4


    def SET2b(self):
        self.R.b |= 0x04
        self.R.m = 2

    def SET2c(self):
        self.R.b |= 0x04
        self.R.m = 2

    def SET2d(self):
        self.R.b |= 0x04
        self.R.m = 2

    def SET2e(self):
        self.R.b |= 0x04
        self.R.m = 2

    def SET2h(self):
        self.R.b |= 0x04
        self.R.m = 2

    def SET2l(self):
        self.R.b |= 0x04
        self.R.m = 2

    def SET2a(self):
        self.R.b |= 0x04
        self.R.m = 2

    def SET2m(self):
        i = self.mainboard.MMU.readByte((self.R.h << 8) + self.R.l)
        i |= 0x04
        self.mainboard.MMU.writeByte((self.R.h << 8) + self.R.l, i)
        self.R.m = 4


    def BIT3b(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.b & 0x08 else 0x80
        self.R.m = 2

    def BIT3c(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.c & 0x08 else 0x80
        self.R.m = 2

    def BIT3d(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.d & 0x08 else 0x80
        self.R.m = 2

    def BIT3e(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.e & 0x08 else 0x80
        self.R.m = 2

    def BIT3h(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.h & 0x08 else 0x80
        self.R.m = 2

    def BIT3l(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.l & 0x08 else 0x80
        self.R.m = 2

    def BIT3a(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.a & 0x08 else 0x80
        self.R.m = 2

    def BIT3m(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.mainboard.MMU.readByte((self.R.h << 8) + self.R.l) & 0x08 else 0x80
        self.R.m = 3


    def RES3b(self):
        self.R.b &= 0xF7
        self.R.m = 2

    def RES3c(self):
        self.R.c &= 0xF7
        self.R.m = 2

    def RES3d(self):
        self.R.d &= 0xF7
        self.R.m = 2

    def RES3e(self):
        self.R.e &= 0xF7
        self.R.m = 2

    def RES3h(self):
        self.R.h &= 0xF7
        self.R.m = 2

    def RES3l(self):
        self.R.l &= 0xF7
        self.R.m = 2

    def RES3a(self):
        self.R.a &= 0xF7
        self.R.m = 2

    def RES3m(self):
        i = self.mainboard.MMU.readByte((self.R.h << 8) + self.R.l)
        i &= 0xF7
        self.mainboard.MMU.writeByte((self.R.h << 8) + self.R.l, i)
        self.R.m = 4


    def SET3b(self):
        self.R.b |= 0x08
        self.R.m = 2

    def SET3c(self):
        self.R.b |= 0x08
        self.R.m = 2

    def SET3d(self):
        self.R.b |= 0x08
        self.R.m = 2

    def SET3e(self):
        self.R.b |= 0x08
        self.R.m = 2

    def SET3h(self):
        self.R.b |= 0x08
        self.R.m = 2

    def SET3l(self):
        self.R.b |= 0x08
        self.R.m = 2

    def SET3a(self):
        self.R.b |= 0x08
        self.R.m = 2

    def SET3m(self):
        i = self.mainboard.MMU.readByte((self.R.h << 8) + self.R.l)
        i |= 0x08
        self.mainboard.MMU.writeByte((self.R.h << 8) + self.R.l, i)
        self.R.m = 4

    # ---
    def BIT4b(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.b & 0x10 else 0x80
        self.R.m = 2

    def BIT4c(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.c & 0x10 else 0x80
        self.R.m = 2

    def BIT4d(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.d & 0x10 else 0x80
        self.R.m = 2

    def BIT4e(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.e & 0x10 else 0x80
        self.R.m = 2

    def BIT4h(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.h & 0x10 else 0x80
        self.R.m = 2

    def BIT4l(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.l & 0x10 else 0x80
        self.R.m = 2

    def BIT4a(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.a & 0x10 else 0x80
        self.R.m = 2

    def BIT4m(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.mainboard.MMU.readByte((self.R.h << 8) + self.R.l) & 0x10 else 0x80
        self.R.m = 3

    # ---
    def RES4b(self):
        self.R.b &= 0xEF
        self.R.m = 2

    def RES4c(self):
        self.R.c &= 0xEF
        self.R.m = 2

    def RES4d(self):
        self.R.d &= 0xEF
        self.R.m = 2

    def RES4e(self):
        self.R.e &= 0xEF
        self.R.m = 2

    def RES4h(self):
        self.R.h &= 0xEF
        self.R.m = 2

    def RES4l(self):
        self.R.l &= 0xEF
        self.R.m = 2

    def RES4a(self):
        self.R.a &= 0xEF
        self.R.m = 2

    def RES4m(self):
        i = self.mainboard.MMU.readByte((self.R.h << 8) + self.R.l)
        i &= 0xEF
        self.mainboard.MMU.writeByte((self.R.h << 8) + self.R.l, i)
        self.R.m = 4

    # ---
    def SET4b(self):
        self.R.b |= 0x10
        self.R.m = 2

    def SET4c(self):
        self.R.b |= 0x10
        self.R.m = 2

    def SET4d(self):
        self.R.b |= 0x10
        self.R.m = 2

    def SET4e(self):
        self.R.b |= 0x10
        self.R.m = 2

    def SET4h(self):
        self.R.b |= 0x10
        self.R.m = 2

    def SET4l(self):
        self.R.b |= 0x10
        self.R.m = 2

    def SET4a(self):
        self.R.b |= 0x10
        self.R.m = 2

    def SET4m(self):
        i = self.mainboard.MMU.readByte((self.R.h << 8) + self.R.l)
        i |= 0x10
        self.mainboard.MMU.writeByte((self.R.h << 8) + self.R.l, i)
        self.R.m = 4

    # ---
    def BIT5b(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.b & 0x20 else 0x80
        self.R.m = 2

    def BIT5c(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.c & 0x20 else 0x80
        self.R.m = 2

    def BIT5d(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.d & 0x20 else 0x80
        self.R.m = 2

    def BIT5e(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.e & 0x20 else 0x80
        self.R.m = 2

    def BIT5h(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.h & 0x20 else 0x80
        self.R.m = 2

    def BIT5l(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.l & 0x20 else 0x80
        self.R.m = 2

    def BIT5a(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.a & 0x20 else 0x80
        self.R.m = 2

    def BIT5m(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.mainboard.MMU.readByte((self.R.h << 8) + self.R.l) & 0x20 else 0x80
        self.R.m = 3

    # ---
    def RES5b(self):
        self.R.b &= 0xDF
        self.R.m = 2

    def RES5c(self):
        self.R.c &= 0xDF
        self.R.m = 2

    def RES5d(self):
        self.R.d &= 0xDF
        self.R.m = 2

    def RES5e(self):
        self.R.e &= 0xDF
        self.R.m = 2

    def RES5h(self):
        self.R.h &= 0xDF
        self.R.m = 2

    def RES5l(self):
        self.R.l &= 0xDF
        self.R.m = 2

    def RES5a(self):
        self.R.a &= 0xDF
        self.R.m = 2

    def RES5m(self):
        i = self.mainboard.MMU.readByte((self.R.h << 8) + self.R.l)
        i &= 0xDF
        self.mainboard.MMU.writeByte((self.R.h << 8) + self.R.l, i)
        self.R.m = 4

    # ---
    def SET5b(self):
        self.R.b |= 0x20
        self.R.m = 2

    def SET5c(self):
        self.R.b |= 0x20
        self.R.m = 2

    def SET5d(self):
        self.R.b |= 0x20
        self.R.m = 2

    def SET5e(self):
        self.R.b |= 0x20
        self.R.m = 2

    def SET5h(self):
        self.R.b |= 0x20
        self.R.m = 2

    def SET5l(self):
        self.R.b |= 0x20
        self.R.m = 2

    def SET5a(self):
        self.R.b |= 0x20
        self.R.m = 2

    def SET5m(self):
        i = self.mainboard.MMU.readByte((self.R.h << 8) + self.R.l)
        i |= 0x20
        self.mainboard.MMU.writeByte((self.R.h << 8) + self.R.l, i)
        self.R.m = 4

    # ---
    def BIT6b(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.b & 0x40 else 0x80
        self.R.m = 2

    def BIT6c(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.c & 0x40 else 0x80
        self.R.m = 2

    def BIT6d(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.d & 0x40 else 0x80
        self.R.m = 2

    def BIT6e(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.e & 0x40 else 0x80
        self.R.m = 2

    def BIT6h(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.h & 0x40 else 0x80
        self.R.m = 2

    def BIT6l(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.l & 0x40 else 0x80
        self.R.m = 2

    def BIT6a(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.a & 0x40 else 0x80
        self.R.m = 2

    def BIT6m(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.mainboard.MMU.readByte((self.R.h << 8) + self.R.l) & 0x40 else 0x80
        self.R.m = 3

    # ---
    def RES6b(self):
        self.R.b &= 0xBF
        self.R.m = 2

    def RES6c(self):
        self.R.c &= 0xBF
        self.R.m = 2

    def RES6d(self):
        self.R.d &= 0xBF
        self.R.m = 2

    def RES6e(self):
        self.R.e &= 0xBF
        self.R.m = 2

    def RES6h(self):
        self.R.h &= 0xBF
        self.R.m = 2

    def RES6l(self):
        self.R.l &= 0xBF
        self.R.m = 2

    def RES6a(self):
        self.R.a &= 0xBF
        self.R.m = 2

    def RES6m(self):
        i = self.mainboard.MMU.readByte((self.R.h << 8) + self.R.l)
        i &= 0xBF
        self.mainboard.MMU.writeByte((self.R.h << 8) + self.R.l, i)
        self.R.m = 4

    # ---
    def SET6b(self):
        self.R.b |= 0x40
        self.R.m = 2

    def SET6c(self):
        self.R.b |= 0x40
        self.R.m = 2

    def SET6d(self):
        self.R.b |= 0x40
        self.R.m = 2

    def SET6e(self):
        self.R.b |= 0x40
        self.R.m = 2

    def SET6h(self):
        self.R.b |= 0x40
        self.R.m = 2

    def SET6l(self):
        self.R.b |= 0x40
        self.R.m = 2

    def SET6a(self):
        self.R.b |= 0x40
        self.R.m = 2

    def SET6m(self):
        i = self.mainboard.MMU.readByte((self.R.h << 8) + self.R.l)
        i |= 0x40
        self.mainboard.MMU.writeByte((self.R.h << 8) + self.R.l, i)
        self.R.m = 4

    # ---
    def BIT7b(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.b & 0x80 else 0x80
        self.R.m = 2

    def BIT7c(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.c & 0x80 else 0x80
        self.R.m = 2

    def BIT7d(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.d & 0x80 else 0x80
        self.R.m = 2

    def BIT7e(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.e & 0x80 else 0x80
        self.R.m = 2

    def BIT7h(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.h & 0x80 else 0x80
        self.R.m = 2

    def BIT7l(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.l & 0x80 else 0x80
        self.R.m = 2

    def BIT7a(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.R.a & 0x80 else 0x80
        self.R.m = 2

    def BIT7m(self):
        self.R.f &= 0x1F
        self.R.f |= 0x20
        self.R.f = 0 if self.mainboard.MMU.readByte((self.R.h << 8) + self.R.l) & 0x80 else 0x80
        self.R.m = 3

    # ---
    def RES7b(self):
        self.R.b &= 0x7F
        self.R.m = 2

    def RES7c(self):
        self.R.c &= 0x7F
        self.R.m = 2

    def RES7d(self):
        self.R.d &= 0x7F
        self.R.m = 2

    def RES7e(self):
        self.R.e &= 0x7F
        self.R.m = 2

    def RES7h(self):
        self.R.h &= 0x7F
        self.R.m = 2

    def RES7l(self):
        self.R.l &= 0x7F
        self.R.m = 2

    def RES7a(self):
        self.R.a &= 0x7F
        self.R.m = 2

    def RES7m(self):
        i = self.mainboard.MMU.readByte((self.R.h << 8) + self.R.l)
        i &= 0x7F
        self.mainboard.MMU.writeByte((self.R.h << 8) + self.R.l, i)
        self.R.m = 4

    # ---
    def SET7b(self):
        self.R.b |= 0x80
        self.R.m = 2

    def SET7c(self):
        self.R.b |= 0x80
        self.R.m = 2

    def SET7d(self):
        self.R.b |= 0x80
        self.R.m = 2

    def SET7e(self):
        self.R.b |= 0x80
        self.R.m = 2

    def SET7h(self):
        self.R.b |= 0x80
        self.R.m = 2

    def SET7l(self):
        self.R.b |= 0x80
        self.R.m = 2

    def SET7a(self):
        self.R.b |= 0x80
        self.R.m = 2

    def SET7m(self):
        i = self.mainboard.MMU.readByte((self.R.h << 8) + self.R.l)
        i |= 0x80
        self.mainboard.MMU.writeByte((self.R.h << 8) + self.R.l, i)
        self.R.m = 4

    # ---
    def RLA(self):
        ci = 1 if self.R.f & 0x10 else 0
        co = 0x10 if self.R.a & 0x80 else 0
        self.R.a = (self.R.a << 1) + ci
        self.R.a &= 255
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 1

    def RLCA(self):
        ci = 1 if self.R.a & 0x80 else 0
        co = 0x10 if self.R.a & 0x80 else 0
        self.R.a = (self.R.a << 1) + ci
        self.R.a &= 255
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 1

    def RRA(self):
        ci = 0x80 if self.R.f & 0x10 else 0
        co = 0x10 if self.R.a & 1 else 0
        self.R.a = (self.R.a >> 1) + ci
        self.R.a &= 255
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 1

    def RRCA(self):
        ci = 0x80 if self.R.a & 1 else 0
        co = 0x10 if self.R.a & 1 else 0
        self.R.a = (self.R.a >> 1) + ci
        self.R.a &= 255
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 1

    # ---
    def RLr_b(self):
        ci = 1 if self.R.f & 0x10 else 0
        co = 0x10 if self.R.b & 0x80 else 0
        self.R.b = (self.R.b << 1) + ci
        self.R.b &= 255
        self.R.f = 0 if self.R.b else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2

    def RLr_c(self):
        ci = 1 if self.R.f & 0x10 else 0
        co = 0x10 if self.R.c & 0x80 else 0
        self.R.c = (self.R.c << 1) + ci
        self.R.c &= 255
        self.R.f = 0 if self.R.c else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2

    def RLr_d(self):
        ci = 1 if self.R.f & 0x10 else 0
        co = 0x10 if self.R.d & 0x80 else 0
        self.R.d = (self.R.d << 1) + ci
        self.R.d &= 255
        self.R.f = 0 if self.R.d else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2

    def RLr_e(self):
        ci = 1 if self.R.f & 0x10 else 0
        co = 0x10 if self.R.e & 0x80 else 0
        self.R.e = (self.R.e << 1) + ci
        self.R.e &= 255
        self.R.f = 0 if self.R.e else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2

    def RLr_h(self):
        ci = 1 if self.R.f & 0x10 else 0
        co = 0x10 if self.R.h & 0x80 else 0
        self.R.h = (self.R.h << 1) + ci
        self.R.h &= 255
        self.R.f = 0 if self.R.h else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2

    def RLr_l(self):
        ci = 1 if self.R.f & 0x10 else 0
        co = 0x10 if self.R.l & 0x80 else 0
        self.R.l = (self.R.l << 1) + ci
        self.R.l &= 255
        self.R.f = 0 if self.R.l else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2

    def RLr_a(self):
        ci = 1 if self.R.f & 0x10 else 0
        co = 0x10 if self.R.a & 0x80 else 0
        self.R.a = (self.R.a << 1) + ci
        self.R.a &= 255
        self.R.f = 0 if self.R.a else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2

    def RLHL(self):
        i = self.mainboard.MMU.readByte((self.R.h << 8) + self.R.l)
        ci = 1 if self.R.f & 0x10 else 0
        co = 0x10 if i & 0x80 else 0
        i = (i << 1) + ci
        i &= 255
        self.R.f = 0 if i else 0x80
        self.mainboard.MMU.writeByte((self.R.h << 8) + self.R.l, i)
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 4


    def RLCr_b(self):
        ci = 1 if self.R.b & 0x80 else 0
        co = 0x10 if self.R.b & 0x80 else 0
        self.R.b = (self.R.b << 1) + ci
        self.R.b &= 255
        self.R.f = 0 if self.R.b else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2

    def RLCr_c(self):
        ci = 1 if self.R.c & 0x80 else 0
        co = 0x10 if self.R.c & 0x80 else 0
        self.R.c = (self.R.c << 1) + ci
        self.R.c &= 255
        self.R.f = 0 if self.R.c else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2

    def RLCr_d(self):
        ci = 1 if self.R.d & 0x80 else 0
        co = 0x10 if self.R.d & 0x80 else 0
        self.R.d = (self.R.d << 1) + ci
        self.R.d &= 255
        self.R.f = 0 if self.R.d else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2

    def RLCr_e(self):
        ci = 1 if self.R.e & 0x80 else 0
        co = 0x10 if self.R.e & 0x80 else 0
        self.R.e = (self.R.e << 1) + ci
        self.R.e &= 255
        self.R.f = 0 if self.R.e else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2

    def RLCr_h(self):
        ci = 1 if self.R.h & 0x80 else 0
        co = 0x10 if self.R.h & 0x80 else 0
        self.R.h = (self.R.h << 1) + ci
        self.R.h &= 255
        self.R.f = 0 if self.R.h else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2

    def RLCr_l(self):
        ci = 1 if self.R.l & 0x80 else 0
        co = 0x10 if self.R.l & 0x80 else 0
        self.R.l = (self.R.l << 1) + ci
        self.R.l &= 255
        self.R.f = 0 if self.R.l else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2

    def RLCr_a(self):
        ci = 1 if self.R.a & 0x80 else 0
        co = 0x10 if self.R.a & 0x80 else 0
        self.R.a = (self.R.a << 1) + ci
        self.R.a &= 255
        self.R.f = 0 if self.R.a else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2

    def RLCHL(self):
        i = self.mainboard.MMU.readByte((self.R.h << 8) + self.R.l)
        ci = 1 if i & 0x80 else 0
        co = 0x10 if i & 0x80 else 0
        i = (i << 1) + ci
        i &= 255
        self.R.f = 0 if i else 0x80
        self.mainboard.MMU.writeByte((self.R.h << 8) + self.R.l, i)
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 4


    def RRr_b(self):
        ci = 0x80 if self.R.f & 0x10 else 0
        co = 0x10 if self.R.b & 1 else 0
        self.R.b = (self.R.b >> 1) + ci
        self.R.b &= 255
        self.R.f = 0 if self.R.b else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2

    def RRr_c(self):
        ci = 0x80 if self.R.f & 0x10 else 0
        co = 0x10 if self.R.c & 1 else 0
        self.R.c = (self.R.c >> 1) + ci
        self.R.c &= 255
        self.R.f = 0 if self.R.c else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2

    def RRr_d(self):
        ci = 0x80 if self.R.f & 0x10 else 0
        co = 0x10 if self.R.d & 1 else 0
        self.R.d = (self.R.d >> 1) + ci
        self.R.d &= 255
        self.R.f = 0 if self.R.d else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2

    def RRr_e(self):
        ci = 0x80 if self.R.f & 0x10 else 0
        co = 0x10 if self.R.e & 1 else 0
        self.R.e = (self.R.e >> 1) + ci
        self.R.e &= 255
        self.R.f = 0 if self.R.e else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2

    def RRr_h(self):
        ci = 0x80 if self.R.f & 0x10 else 0
        co = 0x10 if self.R.h & 1 else 0
        self.R.h = (self.R.h >> 1) + ci
        self.R.h &= 255
        self.R.f = 0 if self.R.h else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2

    def RRr_l(self):
        ci = 0x80 if self.R.f & 0x10 else 0
        co = 0x10 if self.R.l & 1 else 0
        self.R.l = (self.R.l >> 1) + ci
        self.R.l &= 255
        self.R.f = 0 if self.R.l else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2

    def RRr_a(self):
        ci = 0x80 if self.R.f & 0x10 else 0
        co = 0x10 if self.R.a & 1 else 0
        self.R.a = (self.R.a >> 1) + ci
        self.R.a &= 255
        self.R.f = 0 if self.R.a else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2

    def RRHL(self):
        i = self.mainboard.MMU.readByte((self.R.h << 8) + self.R.l)
        ci = 0x80 if self.R.f & 0x10 else 0
        co = 0x10 if i & 1 else 0
        i = (i >> 1) + ci
        i &= 255
        self.mainboard.MMU.writeByte((self.R.h << 8) + self.R.l, i)
        self.R.f = 0 if i else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 4


    def RRCr_b(self):
        ci = 0x80 if self.R.b & 1 else 0
        co = 0x10 if self.R.b & 1 else 0
        self.R.b = (self.R.b >> 1) + ci
        self.R.b &= 255
        self.R.f = 0 if self.R.b else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2

    def RRCr_c(self):
        ci = 0x80 if self.R.c & 1 else 0
        co = 0x10 if self.R.c & 1 else 0
        self.R.c = (self.R.c >> 1) + ci
        self.R.c &= 255
        self.R.f = 0 if self.R.c else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2

    def RRCr_d(self):
        ci = 0x80 if self.R.d & 1 else 0
        co = 0x10 if self.R.d & 1 else 0
        self.R.d = (self.R.d >> 1) + ci
        self.R.d &= 255
        self.R.f = 0 if self.R.d else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2

    def RRCr_e(self):
        ci = 0x80 if self.R.e & 1 else 0
        co = 0x10 if self.R.e & 1 else 0
        self.R.e = (self.R.e >> 1) + ci
        self.R.e &= 255
        self.R.f = 0 if self.R.e else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2

    def RRCr_h(self):
        ci = 0x80 if self.R.h & 1 else 0
        co = 0x10 if self.R.h & 1 else 0
        self.R.h = (self.R.h >> 1) + ci
        self.R.h &= 255
        self.R.f = 0 if self.R.h else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2

    def RRCr_l(self):
        ci = 0x80 if self.R.l & 1 else 0
        co = 0x10 if self.R.l & 1 else 0
        self.R.l = (self.R.l >> 1) + ci
        self.R.l &= 255
        self.R.f = 0 if self.R.l else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2

    def RRCr_a(self):
        ci = 0x80 if self.R.a & 1 else 0
        co = 0x10 if self.R.a & 1 else 0
        self.R.a = (self.R.a >> 1) + ci
        self.R.a &= 255
        self.R.f = 0 if self.R.a else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2

    def RRCHL(self):
        i = self.mainboard.MMU.readByte((self.R.h << 8) + self.R.l)
        ci = 0x80 if i & 1 else 0
        co = 0x10 if i & 1 else 0
        i = (i >> 1) + ci
        i &= 255
        self.mainboard.MMU.writeByte((self.R.h << 8) + self.R.l, i)
        self.R.f = 0 if i else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 4


    def SLAr_b(self):
        co = 0x10 if self.R.b & 0x80 else 0
        self.R.b = (self.R.b << 1) & 255
        self.R.f = 0 if self.R.b else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2

    def SLAr_c(self):
        co = 0x10 if self.R.c & 0x80 else 0
        self.R.c = (self.R.c << 1) & 255
        self.R.f = 0 if self.R.c else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2

    def SLAr_d(self):
        co = 0x10 if self.R.d & 0x80 else 0
        self.R.d = (self.R.d << 1) & 255
        self.R.f = 0 if self.R.d else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2

    def SLAr_e(self):
        co = 0x10 if self.R.e & 0x80 else 0
        self.R.e = (self.R.e << 1) & 255
        self.R.f = 0 if self.R.e else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2

    def SLAr_h(self):
        co = 0x10 if self.R.h & 0x80 else 0
        self.R.h = (self.R.h << 1) & 255
        self.R.f = 0 if self.R.h else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2

    def SLAr_l(self):
        co = 0x10 if self.R.l & 0x80 else 0
        self.R.l = (self.R.l << 1) & 255
        self.R.f = 0 if self.R.l else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2

    def SLAr_a(self):
        co = 0x10 if self.R.a & 0x80 else 0
        self.R.a = (self.R.a << 1) & 255
        self.R.f = 0 if self.R.a else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2


    def SLLr_b(self):
        co = 0x10 if self.R.b & 0x80 else 0
        self.R.b = (self.R.b << 1) & 255 + 1
        self.R.f = 0 if self.R.b else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2

    def SLLr_c(self):
        co = 0x10 if self.R.c & 0x80 else 0
        self.R.c = (self.R.c << 1) & 255 + 1
        self.R.f = 0 if self.R.c else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2

    def SLLr_d(self):
        co = 0x10 if self.R.d & 0x80 else 0
        self.R.d = (self.R.d << 1) & 255 + 1
        self.R.f = 0 if self.R.d else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2

    def SLLr_e(self):
        co = 0x10 if self.R.e & 0x80 else 0
        self.R.e = (self.R.e << 1) & 255 + 1
        self.R.f = 0 if self.R.e else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2

    def SLLr_h(self):
        co = 0x10 if self.R.h & 0x80 else 0
        self.R.h = (self.R.h << 1) & 255 + 1
        self.R.f = 0 if self.R.h else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2

    def SLLr_l(self):
        co = 0x10 if self.R.l & 0x80 else 0
        self.R.l = (self.R.l << 1) & 255 + 1
        self.R.f = 0 if self.R.l else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2

    def SLLr_a(self):
        co = 0x10 if self.R.a & 0x80 else 0
        self.R.a = (self.R.a << 1) & 255 + 1
        self.R.f = 0 if self.R.a else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2


    def SRAr_b(self):
        ci = self.R.b & 0x80
        co = 0x10 if self.R.b & 1 else 0
        self.R.b = ((self.R.b >> 1) + ci) & 255
        self.R.f = 0 if self.R.b else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2

    def SRAr_c(self):
        ci = self.R.c & 0x80
        co = 0x10 if self.R.c & 1 else 0
        self.R.c = ((self.R.c >> 1) + ci) & 255
        self.R.f = 0 if self.R.c else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2

    def SRAr_d(self):
        ci = self.R.d & 0x80
        co = 0x10 if self.R.d & 1 else 0
        self.R.d = ((self.R.d >> 1) + ci) & 255
        self.R.f = 0 if self.R.d else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2

    def SRAr_e(self):
        ci = self.R.e & 0x80
        co = 0x10 if self.R.e & 1 else 0
        self.R.e = ((self.R.e >> 1) + ci) & 255
        self.R.f = 0 if self.R.e else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2

    def SRAr_h(self):
        ci = self.R.h & 0x80
        co = 0x10 if self.R.h & 1 else 0
        self.R.h = ((self.R.h >> 1) + ci) & 255
        self.R.f = 0 if self.R.h else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2

    def SRAr_l(self):
        ci = self.R.l & 0x80
        co = 0x10 if self.R.l & 1 else 0
        self.R.l = ((self.R.l >> 1) + ci) & 255
        self.R.f = 0 if self.R.l else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2

    def SRAr_a(self):
        ci = self.R.a & 0x80
        co = 0x10 if self.R.a & 1 else 0
        self.R.a = ((self.R.a >> 1) + ci) & 255
        self.R.f = 0 if self.R.a else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2


    def SRLr_b(self):
        co = 0x10 if self.R.b & 1 else 0
        self.R.b = (self.R.b >> 1) & 255
        self.R.f = 0 if self.R.b else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2

    def SRLr_c(self):
        co = 0x10 if self.R.c & 1 else 0
        self.R.c = (self.R.c >> 1) & 255
        self.R.f = 0 if self.R.c else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2

    def SRLr_d(self):
        co = 0x10 if self.R.d & 1 else 0
        self.R.d = (self.R.d >> 1) & 255
        self.R.f = 0 if self.R.d else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2

    def SRLr_e(self):
        co = 0x10 if self.R.e & 1 else 0
        self.R.e = (self.R.e >> 1) & 255
        self.R.f = 0 if self.R.e else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2

    def SRLr_h(self):
        co = 0x10 if self.R.h & 1 else 0
        self.R.h = (self.R.h >> 1) & 255
        self.R.f = 0 if self.R.h else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2

    def SRLr_l(self):
        co = 0x10 if self.R.l & 1 else 0
        self.R.l = (self.R.l >> 1) & 255
        self.R.f = 0 if self.R.l else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2

    def SRLr_a(self):
        co = 0x10 if self.R.a & 1 else 0
        self.R.a = (self.R.a >> 1) & 255
        self.R.f = 0 if self.R.a else 0x80
        self.R.f = (self.R.f & 0xEF) + co
        self.R.m = 2


    def CPL(self):
        self.R.a ^= 255
        self.R.f = 0 if self.R.a else 0x80
        self.R.m = 1

    def NEG(self):
        self.R.a = 0 - self.R.a
        self.R.f = 0x10 if self.R.a < 0 else 0
        self.R.a &= 255
        if not self.R.a:
            self.R.f |= 0x80
        self.R.m = 2


    def CCF(self):
        ci = 0 if self.R.f & 0x10 else 0x10
        self.R.f = (self.R.f & 0xEF) + ci
        self.R.m = 1

    def SCF(self):
        self.R.f |= 0x10
        self.R.m = 1


        # --- Stack ---

    def PUSHBC(self):
        self.R.sp -= 1
        self.mainboard.MMU.writeByte(self.R.sp, self.R.b)
        self.R.sp -= 1
        self.mainboard.MMU.writeByte(self.R.sp, self.R.c)
        self.R.m = 3

    def PUSHDE(self):
        self.R.sp -= 1
        self.mainboard.MMU.writeByte(self.R.sp, self.R.d)
        self.R.sp -= 1
        self.mainboard.MMU.writeByte(self.R.sp, self.R.e)
        self.R.m = 3

    def PUSHHL(self):
        self.R.sp -= 1
        self.mainboard.MMU.writeByte(self.R.sp, self.R.h)
        self.R.sp -= 1
        self.mainboard.MMU.writeByte(self.R.sp, self.R.l)
        self.R.m = 3

    def PUSHAF(self):
        self.R.sp -= 1
        self.mainboard.MMU.writeByte(self.R.sp, self.R.a)
        self.R.sp -= 1
        self.mainboard.MMU.writeByte(self.R.sp, self.R.f)
        self.R.m = 3


    def POPBC(self):
        self.R.c = self.mainboard.MMU.readByte(self.R.sp)
        self.R.sp += 1
        self.R.b = self.mainboard.MMU.readByte(self.R.sp)
        self.R.sp += 1
        self.R.m = 3

    def POPDE(self):
        self.R.e = self.mainboard.MMU.readByte(self.R.sp)
        self.R.sp += 1
        self.R.d = self.mainboard.MMU.readByte(self.R.sp)
        self.R.sp += 1
        self.R.m = 3

    def POPHL(self):
        self.R.l = self.mainboard.MMU.readByte(self.R.sp)
        self.R.sp += 1
        self.R.h = self.mainboard.MMU.readByte(self.R.sp)
        self.R.sp += 1
        self.R.m = 3

    def POPAF(self):
        self.R.f = self.mainboard.MMU.readByte(self.R.sp)
        self.R.sp += 1
        self.R.a = self.mainboard.MMU.readByte(self.R.sp)
        self.R.sp += 1
        self.R.m = 3


        # --- Jump ---

    def JPnn(self):
        self.R.pc = self.mainboard.MMU.readWord(self.R.pc)
        self.R.m = 3

    def JPHL(self):
        self.R.pc = (self.R.h << 8) + self.R.l
        self.R.m = 1

    def JPNZnn(self):
        self.R.m = 3
        if (self.R.f & 0x80) == 0x00:
            self.R.pc = self.mainboard.MMU.readWord(self.R.pc)
            self.R.m += 1
        else:
            self.R.pc += 2

    def JPZnn(self):
        self.R.m = 3
        if (self.R.f & 0x80) == 0x80:
            self.R.pc = self.mainboard.MMU.readWord(self.R.pc)
            self.R.m += 1
        else:
            self.R.pc += 2

    def JPNCnn(self):
        self.R.m = 3
        if (self.R.f & 0x10) == 0x00:
            self.R.pc = self.mainboard.MMU.readWord(self.R.pc)
            self.R.m += 1
        else:
            self.R.pc += 2

    def JPCnn(self):
        self.R.m = 3
        if (self.R.f & 0x10) == 0x10:
            self.R.pc = self.mainboard.MMU.readWord(self.R.pc)
            self.R.m += 1
        else:
            self.R.pc += 2


    def JRn(self):
        i = self.mainboard.MMU.readByte(self.R.pc)
        if i > 127:
            i = -((~i + 1) & 255)
        self.R.pc += 1
        self.R.m = 2
        self.R.pc += i
        self.R.m += 1

    def JRNZn(self):
        i = self.mainboard.MMU.readByte(self.R.pc)
        if i > 127:
            i = -((~i + 1) & 255)
        self.R.pc += 1
        self.R.m = 2
        if (self.R.f & 0x80) == 0x00:
            self.R.pc += i
            self.R.m += 1

    def JRZn(self):
        i = self.mainboard.MMU.readByte(self.R.pc)
        if i > 127:
            i = -((~i + 1) & 255)
        self.R.pc += 1
        self.R.m = 2
        if (self.R.f & 0x80) == 0x80:
            self.R.pc += i
            self.R.m += 1

    def JRNCn(self):
        i = self.mainboard.MMU.readByte(self.R.pc)
        if i > 127:
            i = -((~i + 1) & 255)
        self.R.pc += 1
        self.R.m = 2
        if (self.R.f & 0x10) == 0x00:
            self.R.pc += i
            self.R.m += 1

    def JRCn(self):
        i = self.mainboard.MMU.readByte(self.R.pc)
        if i > 127:
            i = -((~i + 1) & 255)
        self.R.pc += 1
        self.R.m = 2
        if (self.R.f & 0x10) == 0x10:
            self.R.pc += i
            self.R.m += 1


    def DJNZn(self):
        i = self.mainboard.MMU.readByte(self.R.pc)
        if i > 127:
            i = -((~i + 1) & 255)
        self.R.pc += 1
        self.R.m = 2
        self.R.b -= 1
        if self.R.b:
            self.R.pc += i
            self.R.m += 1

    def CALLnn(self):
        self.R.sp -= 2
        self.mainboard.MMU.writeWord(self.R.sp, self.R.pc + 2)
        self.R.pc = self.mainboard.MMU.readWord(self.R.pc)
        self.R.m = 5

    def CALLNZnn(self):
        self.R.m = 3
        if (self.R.f & 0x80) == 0x00:
            self.R.sp -= 2
            self.mainboard.MMU.writeWord(self.R.sp, self.R.pc + 2)
            self.R.pc = self.mainboard.MMU.readWord(self.R.pc)
            self.R.m += 2
        else:
            self.R.pc += 2

    def CALLZnn(self):
        self.R.m = 3
        if (self.R.f & 0x80) == 0x80:
            self.R.sp -= 2
            self.mainboard.MMU.writeWord(self.R.sp, self.R.pc + 2)
            self.R.pc = self.mainboard.MMU.readWord(self.R.pc)
            self.R.m += 2
        else:
            self.R.pc += 2

    def CALLNCnn(self):
        self.R.m = 3
        if (self.R.f & 0x10) == 0x00:
            self.R.sp -= 2
            self.mainboard.MMU.writeWord(self.R.sp, self.R.pc + 2)
            self.R.pc = self.mainboard.MMU.readWord(self.R.pc)
            self.R.m += 2
        else:
            self.R.pc += 2

    def CALLCnn(self):
        self.R.m = 3
        if (self.R.f & 0x10) == 0x10:
            self.R.sp -= 2
            self.mainboard.MMU.writeWord(self.R.sp, self.R.pc + 2)
            self.R.pc = self.mainboard.MMU.readWord(self.R.pc)
            self.R.m += 2
        else:
            self.R.pc += 2


    def RET(self):
        self.R.pc = self.mainboard.MMU.readWord(self.R.sp)
        self.R.sp += 2
        self.R.m = 3

    def RETI(self):
        self.R.ime = 1
        self.rrs()
        self.R.pc = self.mainboard.MMU.readWord(self.R.sp)
        self.R.sp += 2
        self.R.m = 3

    def RETNZ(self):
        self.R.m = 1
        if (self.R.f & 0x80) == 0x00:
            self.R.pc = self.mainboard.MMU.readWord(self.R.sp)
            self.R.sp += 2
            self.R.m += 2

    def RETZ(self):
        self.R.m = 1
        if (self.R.f & 0x80) == 0x80:
            self.R.pc = self.mainboard.MMU.readWord(self.R.sp)
            self.R.sp += 2
            self.R.m += 2

    def RETNC(self):
        self.R.m = 1
        if (self.R.f & 0x10) == 0x00:
            self.R.pc = self.mainboard.MMU.readWord(self.R.sp)
            self.R.sp += 2
            self.R.m += 2

    def RETC(self):
        self.R.m = 1
        if (self.R.f & 0x10) == 0x10:
            self.R.pc = self.mainboard.MMU.readWord(self.R.sp)
            self.R.sp += 2
            self.R.m += 2


    def RST00(self):
        self.rsv()
        self.R.sp -= 2
        self.mainboard.MMU.writeWord(self.R.sp, self.R.pc)
        self.R.pc = 0x00
        self.R.m = 3

    def RST08(self):
        self.rsv()
        self.R.sp -= 2
        self.mainboard.MMU.writeWord(self.R.sp, self.R.pc)
        self.R.pc = 0x08
        self.R.m = 3

    def RST10(self):
        self.rsv()
        self.R.sp -= 2
        self.mainboard.MMU.writeWord(self.R.sp, self.R.pc)
        self.R.pc = 0x10
        self.R.m = 3

    def RST18(self):
        self.rsv()
        self.R.sp -= 2
        self.mainboard.MMU.writeWord(self.R.sp, self.R.pc)
        self.R.pc = 0x18
        self.R.m = 3

    def RST20(self):
        self.rsv()
        self.R.sp -= 2
        self.mainboard.MMU.writeWord(self.R.sp, self.R.pc)
        self.R.pc = 0x20
        self.R.m = 3

    def RST28(self):
        self.rsv()
        self.R.sp -= 2
        self.mainboard.MMU.writeWord(self.R.sp, self.R.pc)
        self.R.pc = 0x28
        self.R.m = 3

    def RST30(self):
        self.rsv()
        self.R.sp -= 2
        self.mainboard.MMU.writeWord(self.R.sp, self.R.pc)
        self.R.pc = 0x30
        self.R.m = 3

    def RST38(self):
        self.rsv()
        self.R.sp -= 2
        self.mainboard.MMU.writeWord(self.R.sp, self.R.pc)
        self.R.pc = 0x38
        self.R.m = 3

    def RST40(self):
        self.rsv()
        self.R.sp -= 2
        self.mainboard.MMU.writeWord(self.R.sp, self.R.pc)
        self.R.pc = 0x40
        self.R.m = 3

    def RST48(self):
        self.rsv()
        self.R.sp -= 2
        self.mainboard.MMU.writeWord(self.R.sp, self.R.pc)
        self.R.pc = 0x48
        self.R.m = 3

    def RST50(self):
        self.rsv()
        self.R.sp -= 2
        self.mainboard.MMU.writeWord(self.R.sp, self.R.pc)
        self.R.pc = 0x50
        self.R.m = 3

    def RST58(self):
        self.rsv()
        self.R.sp -= 2
        self.mainboard.MMU.writeWord(self.R.sp, self.R.pc)
        self.R.pc = 0x58
        self.R.m = 3

    def RST60(self):
        self.rsv()
        self.R.sp -= 2
        self.mainboard.MMU.writeWord(self.R.sp, self.R.pc)
        self.R.pc = 0x60
        self.R.m = 3


    def NOP(self):
        self.R.m = 1

    def HALT(self):
        self._HALT = 1
        self.R.m = 1


    def DI(self):
        self.R.ime = 0
        self.R.m = 1

    def EI(self):
        self.R.ime = 1
        self.R.m = 1

    ###
    # Helper function
    ###
    def rsv(self):
        self.RSV.a = self.R.a
        self.RSV.b = self.R.b
        self.RSV.c = self.R.c
        self.RSV.d = self.R.d
        self.RSV.e = self.R.e
        self.RSV.f = self.R.f
        self.RSV.h = self.R.h
        self.RSV.l = self.R.l

    def rrs(self):
        self.R.a = self.RSV.a
        self.R.b = self.RSV.b
        self.R.c = self.RSV.c
        self.R.d = self.RSV.d
        self.R.e = self.RSV.e
        self.R.f = self.RSV.f
        self.R.h = self.RSV.h
        self.R.l = self.RSV.l

    def MAPcb(self):
        i = self.mainboard.MMU.readByte(self.R.pc)
        self.R.pc += 1
        self.R.pc &= 65535
        if self._cbmap[i]:
            self._cbmap[i]()
        else:
            print(i)

    def XX(self):
        """
        Undefined map entry
        """
        opc = self.R.pc - 1
        self._STOP = 1
        raise NotImplementedError('Unimplemented instruction at %i (0x%X)' % (opc, opc))

    def XXX(self, opcode):
        def a():
            raise NotImplementedError('Unimplemented instruction at %i (0x%X)' % (opcode, opcode))
        return a

if __name__ == '__main__':
    a=Processor(None)
    for i,c in enumerate(a._map):
        print('%-4i%-5X%s' % (i, i, c.__name__))