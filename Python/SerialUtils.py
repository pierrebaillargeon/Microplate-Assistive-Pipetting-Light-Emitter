import serial


def write_or_print(bytestring: bytes, serial_connection: serial.Serial):
    if serial_connection:
        serial_connection.write(bytestring)
    else:
        print("Sending bytestring " + str(bytestring))


def get_row_name_from_well(well: str):
    row_name = well[0:1]  # for row
    return row_name


def get_column_number_from_well(well: str):
    column_number = well[1:3]
    return column_number


def send_serial_command(serial_connection: serial.Serial, command: str, barcode: str, well_name: str = None,
                        row: str = None, column: str = None):
    """
    Send a serial command to the given port.
    :param serial_connection: The connection to send a command to. If None, prints out the command instead.
    :param command: The code for the command. X to clear the display, C to light up a column, R to light up a row, S to
    light up a single well, CR to turn off a row, CC to turn off a column, or U to update the display.
    :param barcode: The barcode of the plate.
    :param well_name: The name of the well, which will be used to extract the row and column. Ignored if row and column
    are not None.
    :param row: The row name to give to the command. Can be none to extract from well_name.
    :param column: The column number to give to the command. Can be none to extract from well_name.
    :return:
    """
    if not row:
        row = get_row_name_from_well(well_name)
    if not column:
        column = get_column_number_from_well(well_name)
    serial_string = bytes("<{},{},{},{}>".format(row, column, command, barcode), 'us-ascii')
    write_or_print(serial_string, serial_connection)


def turn_panels_off(*args):
    serial_string = "<A,1,X,>"
    serial_string = bytes(serial_string, 'us-ascii')
    for serial_connection in args:
        write_or_print(serial_string, serial_connection)


def close_connection(*args):
    turn_panels_off(*args)
    for serial_connection in args:
        if serial_connection is not None:
            serial_connection.close()
