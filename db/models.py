# coding: utf-8
from sqlalchemy import BigInteger, Boolean, CHAR, Column, Date, DateTime, Enum, ForeignKey, Index, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class ColChannelType(Base):
    __tablename__ = 'ColChannelType'

    id = Column(String(25), primary_key=True)
    name = Column(String(100), nullable=False, index=True)
    isActive = Column(Boolean, nullable=False, server_default=text("true"))


class ColCommercialStatu(Base):
    __tablename__ = 'ColCommercialStatus'

    id = Column(String(25), primary_key=True)
    description = Column(String(100), nullable=False, index=True)
    isActive = Column(Boolean, nullable=False, server_default=text("true"))


class ColConstructionStatu(Base):
    __tablename__ = 'ColConstructionStatus'

    id = Column(String(25), primary_key=True)
    description = Column(String(100), nullable=False, index=True)
    isActive = Column(Boolean, nullable=False, server_default=text("true"))


class ColCountry(Base):
    __tablename__ = 'ColCountry'

    id = Column(String(25), primary_key=True)
    description = Column(String(100), nullable=False, index=True)
    isActive = Column(Boolean, nullable=False, server_default=text("true"))


class ColMessageType(Base):
    __tablename__ = 'ColMessageType'

    id = Column(String(25), primary_key=True)
    description = Column(String(100), nullable=False, index=True)
    isActive = Column(Boolean, nullable=False, server_default=text("true"))


class ColProjectType(Base):
    __tablename__ = 'ColProjectType'

    id = Column(String(25), primary_key=True)
    description = Column(String(100), nullable=False, index=True)
    isActive = Column(Boolean, nullable=False, server_default=text("true"))


class Conversation(Base):
    __tablename__ = 'Conversation'

    id = Column(String(25), primary_key=True)
    leadId = Column(ForeignKey('Lead.id', ondelete='CASCADE'), nullable=False, index=True)
    acquisitionChannelId = Column(ForeignKey('AcquisitionChannel.id', ondelete='CASCADE'), nullable=False)
    createdAt = Column(TIMESTAMP(precision=6), server_default=text("CURRENT_TIMESTAMP"))
    updatedAt = Column(TIMESTAMP(precision=6), server_default=text("CURRENT_TIMESTAMP"))
    deletedAt = Column(TIMESTAMP(precision=6))

    AcquisitionChannel = relationship('AcquisitionChannel')
    Lead = relationship('Lead', primaryjoin='Conversation.leadId == Lead.id')


class File(Base):
    __tablename__ = 'File'

    id = Column(String(25), primary_key=True)
    type = Column(Enum('image', 'pdf', 'doc', 'xls', 'ppt', 'txt', 'zip', 'other', name='Filetype'), nullable=False)
    name = Column(String(150), nullable=False)
    url = Column(String(255), nullable=False)
    createdAt = Column(TIMESTAMP(precision=6), server_default=text("CURRENT_TIMESTAMP"))
    updatedAt = Column(TIMESTAMP(precision=6), server_default=text("CURRENT_TIMESTAMP"))
    deletedAt = Column(TIMESTAMP(precision=6))


class Lead(Base):
    __tablename__ = 'Lead'

    id = Column(String(25), primary_key=True)
    acquisitionChannelId = Column(ForeignKey('AcquisitionChannel.id', ondelete='RESTRICT'), nullable=False, index=True)
    tenancyId = Column(ForeignKey('Tenancy.id', ondelete='CASCADE'), nullable=False)
    conversionStatus = Column(Enum('contacted', 'interested', 'visited', 'closed', name='ConversionStatus'))
    agentId = Column(ForeignKey('UserWorkspace.id', ondelete='SET NULL'), index=True)
    funnelStatus = Column(Enum('contacted', 'interested', 'visited', 'closed', name='FunnelStatus'), nullable=False, server_default=text("'contacted'::\"FunnelStatus\""))
    interestLevel = Column(Enum('low', 'medium', 'high', name='InterestLevel'), nullable=False, server_default=text("'low'::\"InterestLevel\""))
    createdAt = Column(TIMESTAMP(precision=6), server_default=text("CURRENT_TIMESTAMP"))
    personId = Column(ForeignKey('Person.id', ondelete='RESTRICT'), index=True)
    createdBy = Column(String(25))
    updatedAt = Column(TIMESTAMP(precision=6), server_default=text("CURRENT_TIMESTAMP"))
    updatedBy = Column(String(25))
    previousConversationId = Column(ForeignKey('Conversation.id', ondelete='SET NULL'), index=True)
    currentConversationId = Column(ForeignKey('Conversation.id', ondelete='SET NULL'), index=True)
    deletedAt = Column(TIMESTAMP(precision=6))
    isTemporal = Column(Boolean, nullable=False, server_default=text("false"))

    AcquisitionChannel = relationship('AcquisitionChannel')
    UserWorkspace = relationship('UserWorkspace')
    Conversation = relationship('Conversation', primaryjoin='Lead.currentConversationId == Conversation.id')
    Person = relationship('Person')
    Conversation1 = relationship('Conversation', primaryjoin='Lead.previousConversationId == Conversation.id')
    Tenancy = relationship('Tenancy')


class Migration(Base):
    __tablename__ = 'Migration'
    __table_args__ = (
        Index('ux_migrations_source_updated_ref', 'source', 'updatedAt', 'referenceId', unique=True),
    )

    id = Column(String(25), primary_key=True)
    source = Column(String(150), nullable=False)
    updatedAt = Column(TIMESTAMP(precision=6), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    description = Column(Text)
    referenceId = Column(BigInteger)


class Person(Base):
    __tablename__ = 'Person'

    id = Column(String(25), primary_key=True)
    document = Column(String(20), nullable=False, unique=True)
    lastName = Column(String(100))
    secondLastName = Column(String(100))
    firstNames = Column(String(200))
    birthDate = Column(Date)
    gender = Column(CHAR(1))
    idCard = Column(String(20), unique=True)
    issueDate = Column(Date)
    registrationDate = Column(Date)
    height = Column(Integer)
    age = Column(Integer)
    locationCode = Column(String(50))
    location = Column(String(200))
    address = Column(String(200))
    status = Column(String(50))
    salary = Column(Integer)
    credit = Column(Integer)
    mother = Column(String(200))
    father = Column(String(200))
    state = Column(String(100))
    province = Column(String(100))
    district = Column(String(100))
    phone = Column(String(20), index=True)
    fullName = Column(String(200))
    expirationDate = Column(Date)
    educationLevel = Column(String(100))
    restrictions = Column(Text)
    deletedAt = Column(TIMESTAMP(precision=6))


class Role(Base):
    __tablename__ = 'Role'

    id = Column(String(25), primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    isActive = Column(Boolean, nullable=False, server_default=text("true"))


class WaAttachedFile(Base):
    __tablename__ = 'WaAttachedFile'

    id = Column(String(25), primary_key=True)
    createdAt = Column(TIMESTAMP(precision=6), server_default=text("CURRENT_TIMESTAMP"))
    updatedAt = Column(TIMESTAMP(precision=6), server_default=text("CURRENT_TIMESTAMP"))
    bucket = Column(Text, nullable=False)
    etag = Column(Text, nullable=False)
    filename = Column(String(150), nullable=False)
    mimetype = Column(Text, nullable=False)


class PrismaMigration(Base):
    __tablename__ = '_prisma_migrations'

    id = Column(String(36), primary_key=True)
    checksum = Column(String(64), nullable=False)
    finished_at = Column(DateTime(True))
    migration_name = Column(String(255), nullable=False)
    logs = Column(Text)
    rolled_back_at = Column(DateTime(True))
    started_at = Column(DateTime(True), nullable=False, server_default=text("now()"))
    applied_steps_count = Column(Integer, nullable=False, server_default=text("0"))


class ColRegion(Base):
    __tablename__ = 'ColRegion'

    id = Column(String(25), primary_key=True)
    countryId = Column(ForeignKey('ColCountry.id', ondelete='RESTRICT'), nullable=False, index=True)
    description = Column(String(100), nullable=False, index=True)
    isActive = Column(Boolean, nullable=False, server_default=text("true"))

    ColCountry = relationship('ColCountry')


class SenderWa(Base):
    __tablename__ = 'SenderWa'

    id = Column(String(40), primary_key=True)
    countryCode = Column(String(10), nullable=False)
    number = Column(String(20), nullable=False)
    leadId = Column(ForeignKey('Lead.id', ondelete='CASCADE'), nullable=False, index=True)
    createdAt = Column(TIMESTAMP(precision=6), server_default=text("CURRENT_TIMESTAMP"))
    updatedAt = Column(TIMESTAMP(precision=6), server_default=text("CURRENT_TIMESTAMP"))
    deletedAt = Column(TIMESTAMP(precision=6))

    Lead = relationship('Lead')


class ColProvince(Base):
    __tablename__ = 'ColProvince'

    id = Column(String(25), primary_key=True)
    regionId = Column(ForeignKey('ColRegion.id', ondelete='RESTRICT'), nullable=False, index=True)
    description = Column(String(100), nullable=False, index=True)
    isActive = Column(Boolean, nullable=False, server_default=text("true"))

    ColRegion = relationship('ColRegion')


class ColDistrict(Base):
    __tablename__ = 'ColDistrict'

    id = Column(String(25), primary_key=True)
    provinceId = Column(ForeignKey('ColProvince.id', ondelete='RESTRICT'), nullable=False, index=True)
    description = Column(String(100), nullable=False, index=True)
    isActive = Column(Boolean, nullable=False, server_default=text("true"))

    ColProvince = relationship('ColProvince')


class Company(Base):
    __tablename__ = 'Company'

    id = Column(String(25), primary_key=True)
    legalName = Column(String(100), nullable=False, index=True)
    legalId = Column(String(30))
    tradeName = Column(String(50))
    companyLegalType = Column(Enum('sac', 'sa', 'eirl', name='LegalType'), nullable=False)
    companySize = Column(Enum('micro', 'small', 'medium', 'large', name='CompanySize'))
    activityStartDate = Column(Date)
    numberOfWorkers = Column(Integer)
    address = Column(String(150), nullable=False)
    districtId = Column(ForeignKey('ColDistrict.id', ondelete='SET NULL'), index=True)
    provinceId = Column(ForeignKey('ColProvince.id', ondelete='SET NULL'), index=True)
    countryId = Column(ForeignKey('ColCountry.id', ondelete='SET NULL'), index=True)
    deletedAt = Column(TIMESTAMP(precision=6))
    isActive = Column(Boolean, nullable=False, server_default=text("true"))

    ColCountry = relationship('ColCountry')
    ColDistrict = relationship('ColDistrict')
    ColProvince = relationship('ColProvince')


class Tenancy(Base):
    __tablename__ = 'Tenancy'

    id = Column(String(25), primary_key=True)
    companyId = Column(ForeignKey('Company.id', ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String(100))
    description = Column(String(100))
    createdAt = Column(TIMESTAMP(precision=6), server_default=text("CURRENT_TIMESTAMP"))
    updatedAt = Column(TIMESTAMP(precision=6), server_default=text("CURRENT_TIMESTAMP"))
    deletedAt = Column(TIMESTAMP(precision=6))

    Company = relationship('Company')


class AuthUser(Base):
    __tablename__ = 'AuthUser'

    id = Column(String(25), primary_key=True)
    password = Column(String(128), nullable=False)
    lastLogin = Column(TIMESTAMP(precision=6))
    isSuperuser = Column(Boolean, nullable=False)
    username = Column(String(150), nullable=False, unique=True)
    firstName = Column(String(150), nullable=False)
    lastName = Column(String(150), nullable=False)
    email = Column(String(254), nullable=False)
    isStaff = Column(Boolean, nullable=False)
    isActive = Column(Boolean, nullable=False)
    dateJoined = Column(TIMESTAMP(precision=6), nullable=False)
    tenancyId = Column(ForeignKey('Tenancy.id', ondelete='CASCADE'), index=True)

    Tenancy = relationship('Tenancy')


class BusinessWaNumber(Base):
    __tablename__ = 'BusinessWaNumber'

    id = Column(String(25), primary_key=True)
    countryCode = Column(String(10), nullable=False)
    number = Column(String(10), nullable=False)
    tenancyId = Column(ForeignKey('Tenancy.id', ondelete='CASCADE'), nullable=False, index=True)
    createdAt = Column(TIMESTAMP(precision=6), server_default=text("CURRENT_TIMESTAMP"))
    updatedAt = Column(TIMESTAMP(precision=6), server_default=text("CURRENT_TIMESTAMP"))
    deletedAt = Column(TIMESTAMP(precision=6))

    Tenancy = relationship('Tenancy')


class Project(Base):
    __tablename__ = 'Project'

    id = Column(String(25), primary_key=True)
    tenancyId = Column(ForeignKey('Tenancy.id', ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String(100))
    address = Column(String(100))
    slug = Column(String(60))
    shortCode = Column(String(50))
    districtId = Column(ForeignKey('ColDistrict.id', ondelete='RESTRICT'))
    countryId = Column(ForeignKey('ColCountry.id', ondelete='RESTRICT'))
    constructionStatus = Column(Enum('in_construction', 'finished', name='ProjectConstructionStatus'), nullable=False)
    commercialStatus = Column(Enum('in_construction', 'selling', 'delivered', 'ended', name='ProjectCommercialStatus'), nullable=False)
    mainImageUrl = Column(String(200))
    executingCompanyId = Column(ForeignKey('Company.id', ondelete='RESTRICT'), index=True)
    createdAt = Column(TIMESTAMP(precision=6), server_default=text("CURRENT_TIMESTAMP"))
    updatedAt = Column(TIMESTAMP(precision=6), server_default=text("CURRENT_TIMESTAMP"))
    deletedAt = Column(TIMESTAMP(precision=6))
    projectTypeId = Column(ForeignKey('ColProjectType.id', ondelete='RESTRICT'), index=True)

    ColCountry = relationship('ColCountry')
    ColDistrict = relationship('ColDistrict')
    Company = relationship('Company')
    ColProjectType = relationship('ColProjectType')
    Tenancy = relationship('Tenancy')


class Workspace(Base):
    __tablename__ = 'Workspace'

    id = Column(String(25), primary_key=True)
    tenancyId = Column(ForeignKey('Tenancy.id', ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String(80), nullable=False)
    type = Column(String(50))
    createdAt = Column(TIMESTAMP(precision=6), server_default=text("CURRENT_TIMESTAMP"))
    updatedAt = Column(TIMESTAMP(precision=6), server_default=text("CURRENT_TIMESTAMP"))
    deletedAt = Column(TIMESTAMP(precision=6))

    Tenancy = relationship('Tenancy')


class AcquisitionChannel(Base):
    __tablename__ = 'AcquisitionChannel'

    id = Column(String(25), primary_key=True)
    tenancyId = Column(ForeignKey('Tenancy.id', ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    type = Column(Enum('whatsapp', 'facebook', 'email', name='AcquisitionChannelType'), nullable=False, index=True)
    createdAt = Column(TIMESTAMP(precision=6), server_default=text("CURRENT_TIMESTAMP"))
    updatedAt = Column(TIMESTAMP(precision=6), server_default=text("CURRENT_TIMESTAMP"))
    deletedAt = Column(TIMESTAMP(precision=6))
    waId = Column(ForeignKey('BusinessWaNumber.id', ondelete='SET NULL'), unique=True)
    colChannelTypeId = Column(ForeignKey('ColChannelType.id', ondelete='SET NULL', onupdate='CASCADE'))

    ColChannelType = relationship('ColChannelType')
    Tenancy = relationship('Tenancy')
    BusinessWaNumber = relationship('BusinessWaNumber')


class ProjectImage(Base):
    __tablename__ = 'ProjectImage'

    id = Column(String(25), primary_key=True)
    description = Column(Text)
    type = Column(String(50))
    uploadDate = Column(TIMESTAMP(precision=6), server_default=text("CURRENT_TIMESTAMP"))
    fileId = Column(ForeignKey('File.id', ondelete='CASCADE'), nullable=False, index=True)
    projectId = Column(ForeignKey('Project.id', ondelete='CASCADE'), nullable=False, index=True)

    File = relationship('File')
    Project = relationship('Project')


class ProjectLayout(Base):
    __tablename__ = 'ProjectLayout'

    id = Column(String(25), primary_key=True)
    fileId = Column(ForeignKey('File.id', ondelete='CASCADE'), nullable=False, index=True)
    uploadDate = Column(TIMESTAMP(precision=6), server_default=text("CURRENT_TIMESTAMP"))
    projectId = Column(ForeignKey('Project.id', ondelete='CASCADE'), nullable=False, index=True)

    File = relationship('File')
    Project = relationship('Project')


class ProjectUnit(Base):
    __tablename__ = 'ProjectUnit'

    id = Column(String(25), primary_key=True)
    projectId = Column(ForeignKey('Project.id', ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String(50))
    code = Column(String(50))
    type = Column(String(50))
    price = Column(BigInteger)
    commercialStatusId = Column(ForeignKey('ColCommercialStatus.id', ondelete='RESTRICT'), index=True)
    bedroomsCount = Column(Integer)
    bathroomsCount = Column(Integer)
    area = Column(String(50))
    layout = Column(String(50))
    floor = Column(String(50))
    createdAt = Column(TIMESTAMP(precision=6), server_default=text("CURRENT_TIMESTAMP"))
    updatedAt = Column(TIMESTAMP(precision=6), server_default=text("CURRENT_TIMESTAMP"))
    deletedAt = Column(TIMESTAMP(precision=6))

    ColCommercialStatu = relationship('ColCommercialStatu')
    Project = relationship('Project')


class UserProject(Base):
    __tablename__ = 'UserProject'
    __table_args__ = (
        Index('ux_user_project_user_project', 'userId', 'projectId', unique=True),
    )

    id = Column(String(25), primary_key=True)
    userId = Column(ForeignKey('AuthUser.id', ondelete='CASCADE'), nullable=False)
    projectId = Column(ForeignKey('Project.id', ondelete='CASCADE'), nullable=False)
    createdAt = Column(TIMESTAMP(precision=6), server_default=text("CURRENT_TIMESTAMP"))
    updatedAt = Column(TIMESTAMP(precision=6), server_default=text("CURRENT_TIMESTAMP"))

    Project = relationship('Project')
    AuthUser = relationship('AuthUser')


class UserRole(Base):
    __tablename__ = 'UserRole'
    __table_args__ = (
        Index('ux_user_role_workspace_user_role', 'workspaceId', 'userId', 'roleId', unique=True),
    )

    id = Column(String(25), primary_key=True)
    userId = Column(ForeignKey('AuthUser.id', ondelete='CASCADE'), nullable=False)
    roleId = Column(ForeignKey('Role.id', ondelete='RESTRICT'), nullable=False)
    workspaceId = Column(ForeignKey('Workspace.id', ondelete='CASCADE'), nullable=False)
    createdAt = Column(TIMESTAMP(precision=6), server_default=text("CURRENT_TIMESTAMP"))
    updatedAt = Column(TIMESTAMP(precision=6), server_default=text("CURRENT_TIMESTAMP"))

    Role = relationship('Role')
    AuthUser = relationship('AuthUser')
    Workspace = relationship('Workspace')


class UserWorkspace(Base):
    __tablename__ = 'UserWorkspace'
    __table_args__ = (
        Index('idx_user_workspace_workspace_user', 'workspaceId', 'userId', unique=True),
    )

    id = Column(String(25), primary_key=True)
    userId = Column(ForeignKey('AuthUser.id', ondelete='CASCADE'), nullable=False)
    workspaceId = Column(ForeignKey('Workspace.id', ondelete='CASCADE'), nullable=False)
    createdAt = Column(TIMESTAMP(precision=6), server_default=text("CURRENT_TIMESTAMP"))
    updatedAt = Column(TIMESTAMP(precision=6), server_default=text("CURRENT_TIMESTAMP"))

    AuthUser = relationship('AuthUser')
    Workspace = relationship('Workspace')


class WaMessage(Base):
    __tablename__ = 'WaMessage'

    id = Column(String(40), primary_key=True)
    status = Column(Enum('sent', 'delivered', 'read', 'received', name='WaMessageStatus'), nullable=False, server_default=text("'received'::\"WaMessageStatus\""))
    type = Column(Enum('text', 'image', 'video', 'document', 'audio', 'contacts', 'unsupported', name='WaMessageType'), nullable=False, server_default=text("'text'::\"WaMessageType\""))
    fileCount = Column(Integer, nullable=False, server_default=text("0"))
    body = Column(Text, nullable=False)
    segmentsCount = Column(Integer, nullable=False, server_default=text("0"))
    referralNumMedia = Column(Integer, nullable=False, server_default=text("0"))
    senderWaProfileName = Column(String(150), nullable=False)
    businessWaId = Column(ForeignKey('BusinessWaNumber.id', ondelete='RESTRICT'), nullable=False)
    apiVersion = Column(String(30), nullable=False)
    waAttachedFileId = Column(ForeignKey('WaAttachedFile.id', ondelete='SET NULL'))
    hasAttachedFiles = Column(Boolean, nullable=False, server_default=text("false"))
    conversationId = Column(Text, nullable=False)
    leadId = Column(ForeignKey('Lead.id', ondelete='CASCADE'), index=True)
    createdAt = Column(TIMESTAMP(precision=6), server_default=text("CURRENT_TIMESTAMP"))
    updatedAt = Column(TIMESTAMP(precision=6), server_default=text("CURRENT_TIMESTAMP"))
    senderWaId = Column(ForeignKey('SenderWa.id', ondelete='RESTRICT'), nullable=False, index=True)
    senderWaSid = Column(String(40), nullable=False)

    BusinessWaNumber = relationship('BusinessWaNumber')
    Lead = relationship('Lead')
    SenderWa = relationship('SenderWa')
    WaAttachedFile = relationship('WaAttachedFile')


class Activity(Base):
    __tablename__ = 'Activity'

    id = Column(String(25), primary_key=True)
    leadId = Column(ForeignKey('Lead.id', ondelete='CASCADE'), nullable=False, index=True)
    channelId = Column(ForeignKey('AcquisitionChannel.id', ondelete='CASCADE'), nullable=False, index=True)
    activityType = Column(Enum('call', 'email', 'meeting', 'visit', 'other', name='ActivityType'), nullable=False)
    activityDate = Column(TIMESTAMP(precision=6))
    createdAt = Column(TIMESTAMP(precision=6), server_default=text("CURRENT_TIMESTAMP"))
    updatedAt = Column(TIMESTAMP(precision=6), server_default=text("CURRENT_TIMESTAMP"))

    AcquisitionChannel = relationship('AcquisitionChannel')
    Lead = relationship('Lead')


class Message(Base):
    __tablename__ = 'Message'

    id = Column(String(25), primary_key=True)
    waMessageId = Column(ForeignKey('WaMessage.id', ondelete='CASCADE'))
    conversationId = Column(ForeignKey('Conversation.id', ondelete='CASCADE'), nullable=False, index=True)
    messageTypeId = Column(ForeignKey('ColMessageType.id', ondelete='RESTRICT'), nullable=False, index=True)
    createdAt = Column(TIMESTAMP(precision=6), server_default=text("CURRENT_TIMESTAMP"))
    updatedAt = Column(TIMESTAMP(precision=6), server_default=text("CURRENT_TIMESTAMP"))

    Conversation = relationship('Conversation')
    ColMessageType = relationship('ColMessageType')
    WaMessage = relationship('WaMessage')
