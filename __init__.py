from binaryninja import *

# Note that this is a sample plugin and you may need to manually edit it with
# additional functionality. In particular, this example only passes in the
# binary view. If you would like to act on an addres or function you should
# consider using other register_for* functions.

# Add documentation about UI plugin alternatives and potentially getting
# current_* functions

def main(bv):
    import json
    
    file_name = ""
    if '\\' in str(bv.file.original_filename):
    	file_name = bv.file.original_filename.split('\\')[-1]
    else:
    	file_name = bv.file.original_filename.split('/')[-1]
    
    
    def fixdata(obj_list):
        """
        transforms numbers to hexstring and module names to lowercase
        """
        for entry in obj_list:
            # fix addresses
            if "address" in entry:
                entry["address"] = hex(entry["address"])
            if "start" in entry:
                entry["start"] = hex(entry["start"])
            if "end" in entry:
                entry["end"] = hex(entry["end"])
            # fix module name
            if "module" in entry:
                entry["module"] = entry["module"].lower()
    
    def export_json(filename, data, lowercase_modulename=True):   
        # data transformation
        for category in data.values():
            fixdata(category)
    
        with open(filename, "w") as f:
            json.dump(data, f, sort_keys=True, indent=4)
      
    def get_functions_labels():
        print("[+] Collecting function labels and prototypes")
    
        functions = list()
        labels = list()
        prototype_comments = list()
        module_name = file_name
        imagebase = bv.start
    
        for f in bv.functions:
            if f.symbol.type == SymbolType.FunctionSymbol:
                continue
    
            function_entry = dict()
            function_entry["module"] = module_name
            function_entry["manual"] = False
            function_entry["icount"] = 0  # FIXME
            function_entry["start"] = f.start - imagebase
            functions.append(function_entry)
    
            # label
            label_entry = dict()
            label_entry["module"] = module_name
            label_entry["manual"] = False
            label_entry["address"] = f.start - imagebase
            label_entry["text"] = f.symbol.short_name
            labels.append(label_entry)
    
            # function prototype comment
            comment_entry = dict()
            comment_entry["module"] = module_name
            comment_entry["manual"] = False
            comment_entry["address"] = f.start - imagebase
            comment_entry["text"] = f.symbol.name
            prototype_comments.append(comment_entry)
    
        return functions, labels, prototype_comments
    
    def get_data_labels():
        print("[+] Collecting data labels")
    
        labels = list()
        module_name = file_name
        imagebase = bv.start
        
        for symbol in bv.symbols.items():
            label = symbol[0]
            addr = int(str(bv.symbols.get(label)).split('>')[0].split('@')[1].replace('x','').strip(),16)
            
            if label:
                text = label
            else:
                text = None
    
            if text:
                # function label
                label_entry = dict()
                label_entry["module"] = module_name
                label_entry["manual"] = False
                label_entry["address"] = addr - imagebase
                label_entry["text"] = text
                labels.append(label_entry)
    
        return labels 
    
    def get_comments():
        print("[+] Collecting comments")
    
        module_name = file_name
        imagebase = bv.start
    
        comments = list()
    
        for x in range(bv.start, bv.end):
            comment = bv.get_comment_at(x)
            if comment:
                comment_entry = dict()
                comment_entry["module"] = module_name
                comment_entry["address"] = x - imagebase
                comment_entry["manual"] = False
                comment_entry["text"] = comment
                comments.append(comment_entry)
    
        return comments
    
    def exec():
        output_filename = get_open_filename_input("Select output file name")
    
        if "64" in str(bv.arch):
            suffix = ".dd64"
        else:
            suffix = ".dd32"
    
        if not output_filename.endswith(suffix):
            output_filename = output_filename + suffix
        
        functions, function_labels, prototype_comments = get_functions_labels()
        data_labels = get_data_labels()
        comments = get_comments()
    
        data = dict()
        data["labels"] = function_labels + data_labels
        data["comments"] = prototype_comments + comments
        data["functions"] = functions
        
        export_json(output_filename, data)
        print("[+] Done!")

    exec()

PluginCommand.register('BinjaExportTox64dbg', 'Export notations from Binja to x64dbg', main)