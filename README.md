# Supplyr

Inventory monitoring and supplier reordering automation with an audit trail.

**Built with:** UiPath · Python · MySQL · Microsoft Office

**Subject results:** RPA: Distinction  
*Subject grades; individual project marks were not supplied.*

[Watch the demonstration](https://youtu.be/GeLmaBBpvoU)

## What it includes

- UiPath workflow, Python reorder calculator and SQL setup.
- Required purchase-order template with sample Word/PDF/Excel outputs.
- Completed proposal, specification, report deck and demonstration.

## Project status

Workflow and required files checked; full Windows/Office execution not run. A workflow run can send emails and create purchase orders. The collection check parsed the project without triggering those actions.

## Folder guide

| Folder | Contents |
| --- | --- |
| [`src/`](src/) | Original implementation, assets and project configuration |
| [`docs/`](docs/) | Available specifications, proposals, reports, diagrams and project context |

## Run or open

Open `src/project.json` in a compatible UiPath Studio environment and restore its declared activity packages. Configure MySQL/ODBC, Word, Excel, Outlook and compatible Python.

The workflow contains the original `C:\Python314` path. Adjust environment-specific paths and connection details in your runnable copy. Use test recipients and data for a demonstration.

## Supporting documents

| File | Format |
| --- | --- |
| [demo.md](docs/demo.md) | MD |
| [project-context.md](docs/project-context.md) | MD |
| [rpa-supplyr-project-proposal.docx](docs/proposal/rpa-supplyr-project-proposal.docx) | DOCX |
| [rpa-supplyr-project-report-revision-5.pptx](docs/reports-and-presentations/rpa-supplyr-project-report-revision-5.pptx) | PPTX |
| [rpa-cai2c01-rpa-project-specification-ay2627-apr-v2.pdf](docs/specifications/rpa-cai2c01-rpa-project-specification-ay2627-apr-v2.pdf) | PDF |

## Notes

API keys and demonstration passwords detected in the portfolio copies use
placeholders. Configure your own services before running integrations. Original
source credits and bundled third-party licences remain with their files.
