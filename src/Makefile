MCU     = attiny816
F_CPU   = 3333333UL
PORT    = /dev/ttyUSB0
BAUD    = 57600
CC      = avr-gcc
OBJCOPY = avr-objcopy
SIZE    = avr-size
AVRDUDE = avrdude
CFLAGS  = -mmcu=$(MCU) -DF_CPU=$(F_CPU) -Os -Wall -Wextra \
          -funsigned-char -funsigned-bitfields -fpack-struct \
          -fshort-enums -std=gnu11
TARGET  = beacon
all: $(TARGET).hex size
$(TARGET).elf: $(TARGET).c
	$(CC) $(CFLAGS) -o $@ $<
$(TARGET).hex: $(TARGET).elf
	$(OBJCOPY) -O ihex $< $@
size: $(TARGET).elf
	$(SIZE) --mcu=$(MCU) -C $<
flash: $(TARGET).hex
	$(AVRDUDE) -c serialupdi -p $(MCU) -P $(PORT) -b $(BAUD) \
	           -U flash:w:$<:i
read-fuses:
	$(AVRDUDE) -c serialupdi -p $(MCU) -P $(PORT) -b $(BAUD) -v
clean:
	rm -f $(TARGET).elf $(TARGET).hex
.PHONY: all flash read-fuses size clean
