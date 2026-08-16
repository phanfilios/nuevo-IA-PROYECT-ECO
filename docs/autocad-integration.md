# CAD and AutoCAD integration

The MVP CAD interface is DXF only:

```text
EcoPark AI → validated DXF → AutoCAD or compatible CAD application
```

Each output category is placed on an `ECO_*` DXF layer. EcoPark AI does not start, script or control AutoCAD in this version. A future plugin can import a DXF or call the API after its own AutoCAD-specific security and compatibility review.
