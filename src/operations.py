def time_scaling(signal, scaling_factor):
    # Implement time scaling operation
    pass

def amplitude_scaling(signal, scaling_factor):
    # Implement amplitude scaling operation
    pass

def time_shifting(signal, shift_amount):
    # Implement time shifting operation
    pass

def time_reversal(signal):
    # Implement time reversal operation
    pass

def signal_addition(signal1, signal2):
    # Element-wise addition of two signals (lists)
    if len(signal1) != len(signal2):
        raise ValueError("Signals must be of the same length for addition.")
    return [a + b for a, b in zip(signal1, signal2)]

def signal_multiplication(signal1, signal2):
    # Element-wise multiplication of two signals (lists)
    if len(signal1) != len(signal2):
        raise ValueError("Signals must be of the same length for multiplication.")
    return [a * b for a, b in zip(signal1, signal2)]