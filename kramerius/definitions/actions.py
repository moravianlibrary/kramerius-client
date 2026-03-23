from enum import StrEnum


class Action(StrEnum):
    Read = "a_read"
    PdfRead = "a_pdf_read"
    Delete = "a_delete"
    ProcessEdit = "a_process_edit"
    ProcessRead = "a_process_read"
    OwnerProcessEdit = "a_owner_process_edit"
    Index = "a_index"
    RebuildProcessingIndex = "a_rebuild_processing_index"
    Import = "a_import"
    SetAccessibility = "a_set_accessibility"
    ExportCDK = "a_export_cdk"
    Statistics = "a_statistics"
    StatisticsEdit = "a_statistics_edit"
    ExportStatistics = "a_export_statistics"
    ExportReplications = "a_export_replications"
    ImportReplications = "a_import_replications"
    RightsEdit = "a_rights_edit"
    CriteriaRead = "a_criteria_read"
    CollectionsRead = "a_collections_read"
    CollectionsEdit = "a_collections_edit"
    AbleToBePartOfCollections = "a_able_tobe_part_of_collections"
    GenerateNkplogs = "a_generate_nkplogs"
    RolesEdit = "a_roles_edit"
    RolesRead = "a_roles_read"
    AdminRead = "a_admin_read"
    AkubraRead = "a_akubra_read"
    AkubraEdit = "a_akubra_edit"
    SdnntSync = "a_sdnnt_sync"
    ObjectEdit = "a_object_edit"
    AdminApiSpecificationRead = "a_admin_api_specification_read"
    ContentGenerate = "a_content_generate"
    # Deprecated
    UsersEdit = "a_users_edit"
    Export = "export"
    Editor = "editor"
    Administrate = "administrate"
    ExportK4Replications = "export_k4_replications"
    ImportK4Replications = "import_k4_replications"
    RightsAdmin = "rightsadmin"


# Admin REST ``/licenses`` endpoints that mutate data check
# ``RightsResolver`` with ``A_RIGHTS_EDIT`` on the repository PID
# (``LicensesResource.permit``).
# Reads (GET) are not gated the same way in server.
LICENSES_ADMIN_MUTATION_ACTION = Action.RightsEdit

# ``RightsResource``: editing requires ``a_rights_edit`` (repository or object
# path). ``GET .../rights/criteria`` also allows ``a_criteria_read``.
RIGHTS_EDIT_ACTION = Action.RightsEdit
RIGHTS_CRITERIA_READ_ACTION = Action.CriteriaRead

LICENSE_SCOPED = {Action.Read, Action.PdfRead}
OBJECT_TARGETABLE = {
    Action.Read,
    Action.PdfRead,
    Action.Delete,
    Action.Index,
    Action.RebuildProcessingIndex,
    Action.SetAccessibility,
    Action.RightsEdit,
    Action.CollectionsEdit,
    Action.AbleToBePartOfCollections,
}
