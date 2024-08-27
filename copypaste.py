from pysnmp.smi import builder, view, compiler, rfc1902

def load_mibs_from_folder(mib_folder):
    # Create a MibBuilder instance
    mib_builder = builder.MibBuilder()
    
    # Load MIBs from the specified folder
    mib_builder.addMibSources(builder.DirMibSource(mib_folder))
    
    # Compile ASN.1 MIBs into PySNMP Python objects (if needed)
    compiler.addMibCompiler(mib_builder, sources=[mib_folder])
    
    # Load all MIBs from the folder
    mib_builder.loadModules()
    
    return mib_builder

def list_mib_objects(mib_builder):
    mib_view = view.MibViewController(mib_builder)
    
    for mib_module in mib_builder.mibSymbols:
        print(f"\nMIB Module: {mib_module}")
        for mib_object in mib_builder.mibSymbols[mib_module]:
            try:
                oid = rfc1902.ObjectIdentity(mib_module, mib_object).resolveWithMib(mib_view)
                print(f"Object: {mib_object}, OID: {oid}")
            except Exception as e:
                print(f"Could not resolve {mib_object}: {e}")

if __name__ == "__main__":
    mib_folder = input("Enter the path to your MIB folder: ")
    mib_builder = load_mibs_from_folder(mib_folder)
    list_mib_objects(mib_builder)
