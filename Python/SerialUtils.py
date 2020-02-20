import serial


def write_or_print(bytestring, serial_connection: serial.Serial):
    if serial_connection:
        serial_connection.write(bytestring)
    else:
        print("Sending bytestring to {}: {}".format(serial_connection.port, str(bytestring)))


def get_row_name_from_well(well):
    row_name = well[0:1]  # for row
    return row_name


def get_column_number_from_well(well):
    column_number = well[1:3]
    return column_number


def send_serial_command(well_name, serial_connection, barcode):
    row_name = get_row_name_from_well(well_name)
    column_number = get_column_number_from_well(well_name)
    serial_string = "<" + row_name + "," + column_number + ",S," + barcode + ">"
    serial_string = bytes(serial_string, 'us-ascii')
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