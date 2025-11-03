def first_zero(n):
    """
    Mengubah angka atau string angka menjadi string 2 karakter,
    dengan leading zero jika hanya 1 karakter.
    Contoh:
       pad2(1)   -> "01"
       pad2(9)   -> "09"
       pad2(10)  -> "10"
       pad2("3") -> "03"
    """
    s = str(n)
    if len(s) == 1:
        return "0" + s
    else:
        return s
