"""
Java ``RightCriterium`` qualified names (``getQName()``) for rights criteria.

Use enum members when building ``criterium.qname`` in admin rights JSON; the
value is the exact string the server expects.
"""

from enum import StrEnum


class RightsCriterium(StrEnum):
    """Maps readable names to Kramerius criterium ``qname`` strings."""

    Licenses = "cz.incad.kramerius.security.impl.criteria.Licenses"
    LicensesIpFiltered = (
        "cz.incad.kramerius.security.impl.criteria.LicensesIPFiltered"
    )
    LicensesGeoIpFiltered = (
        "cz.incad.kramerius.security.impl.criteria.LicensesGEOIPFiltered"
    )
    PolicyFlag = "cz.incad.kramerius.security.impl.criteria.PolicyFlag"
    DefaultDomainFilter = (
        "cz.incad.kramerius.security.impl.criteria.DefaultDomainFilter"
    )
    Window = "cz.incad.kramerius.security.impl.criteria.Window"
    DefaultIpAddressFilter = (
        "cz.incad.kramerius.security.impl.criteria.DefaultIPAddressFilter"
    )
    PdfDnntLabels = "cz.incad.kramerius.security.impl.criteria.PDFDNNTLabels"
    BenevolentMovingWall = (
        "cz.incad.kramerius.security.impl.criteria.BenevolentMovingWall"
    )
    CoverAndContentFilter = (
        "cz.incad.kramerius.security.impl.criteria.CoverAndContentFilter"
    )
    ReadDnntLabelsIpFiltered = (
        "cz.incad.kramerius.security.impl.criteria.ReadDNNTLabelsIPFiltered"
    )
    NegativeBenevolentModelFilter = (
        "cz.incad.kramerius.security.impl.criteria."
        "NegativeBenevolentModelFilter"
    )
    ReadDnntLabels = "cz.incad.kramerius.security.impl.criteria.ReadDNNTLabels"
    StrictIpAddressFilter = (
        "cz.incad.kramerius.security.impl.criteria.StrictIPAddresFilter"
    )
    MovingWall = "cz.incad.kramerius.security.impl.criteria.MovingWall"
    StrictDomainFilter = (
        "cz.incad.kramerius.security.impl.criteria.StrictDomainFilter"
    )
    PdfProtectedByLicense = (
        "cz.incad.kramerius.security.impl.criteria.PDFProtectedByLicense"
    )
    BenevolentModelFilter = (
        "cz.incad.kramerius.security.impl.criteria.BenevolentModelFilter"
    )
