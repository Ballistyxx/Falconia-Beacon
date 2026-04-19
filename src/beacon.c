/*
 * beacon.c — ATtiny816 coin-cell LED blinker
 *
 * Pot on PC0 (digital input only — no ADC channel on PORTC).
 *   Pot turned down (PC0 low)  → 1 s on / 1 s off blink
 *   Pot turned up   (PC0 high) → LED steady on
 *
 * LED on PB4, active-high.
 * Clock: 3.333 MHz (20 MHz / 6, default fuse)
 */

#include <avr/io.h>
#include <avr/interrupt.h>
#include <avr/sleep.h>

/* ── Timer (TCA0 overflow for blink timing) ──────────────── */

static volatile uint8_t tick_flag;

ISR(TCA0_OVF_vect)
{
    TCA0.SINGLE.INTFLAGS = TCA_SINGLE_OVF_bm;
    tick_flag = 1;
}

static void timer_init(void)
{
    /*
     * ~10 ms tick: 3 333 333 / 64 = 52 083 Hz → PER = 520 → 9.98 ms
     */
    TCA0.SINGLE.PER     = 520;
    TCA0.SINGLE.INTCTRL = TCA_SINGLE_OVF_bm;
    TCA0.SINGLE.CTRLA   = TCA_SINGLE_CLKSEL_DIV64_gc
                         | TCA_SINGLE_ENABLE_bm;
}

/* ── Main ────────────────────────────────────────────────── */

int main(void)
{
    /* LED pin output, start off */
    PORTB.DIRSET = PIN4_bm;
    PORTB.OUTCLR = PIN4_bm;

    /* PC0 as input with internal pull-up enabled */
    PORTC.DIRCLR  = PIN0_bm;
    PORTC.PIN0CTRL = PORT_PULLUPEN_bm;

    timer_init();
    sei();

    set_sleep_mode(SLEEP_MODE_IDLE);

    uint16_t tick_count  = 0;
    uint8_t  led_on      = 0;
    const uint16_t half_period = 100;  /* 100 × 10 ms = 1 s */

    for (;;) {
        sleep_mode();

        if (!tick_flag)
            continue;
        tick_flag = 0;

        uint8_t pot_high = (PORTC.IN & PIN0_bm);

        if (!pot_high) {
            /* Pot turned down → steady off */
            PORTB.OUTCLR = PIN4_bm;
            led_on     = 0;
            tick_count = 0;
        } else {
            /* Pot turned up → blink */
            if (++tick_count >= half_period) {
                tick_count = 0;
                led_on ^= 1;
                if (led_on)
                    PORTB.OUTSET = PIN4_bm;
                else
                    PORTB.OUTCLR = PIN4_bm;
            }
        }
    }
}
