; EcoPark AI MVP manual DXF handoff helper.
; Run APPLOAD, select this file, then type ECOPARKIMPORT.
(defun c:ECOPARKIMPORT (/ path)
  (setq path (getfiled "Select validated EcoPark DXF" "" "dxf" 0))
  (if path
    (command "_.-INSERT" path "0,0" 1 1 0)
    (prompt "\nNo DXF selected.")
  )
  (princ)
)
